from __future__ import annotations

import json
from typing import Any

import httpx
from pydantic import ValidationError

from app.config import settings
from app.schemas import InterruptScoreResult, JudgmentLevel, OpenAIVisionResult


SYSTEM_PROMPT = (
    "You are scoring a harmless joke app called Cut-in-Meter. "
    "Estimate whether it looks like a good moment to talk to the person in the image. "
    "Use only visible, situational cues such as looking focused on a screen, in conversation, eating, "
    "exercising, wearing headphones, driving, sleeping, or appearing idle. "
    "Treat a visible smile, relaxed expression, and open body language as strong positive cues. "
    "If the person is smiling or softly smiling, return blue. "
    "If no face is visible, or if you cannot see the person's face well enough to judge expression, return red. "
    "Do not infer sensitive traits or identity. Do not guess health status, disability, ethnicity, religion, "
    "age, gender identity, socioeconomic class, or private attributes. "
    "If the scene is ambiguous but a face is visible, prefer a middle score rather than an overly strict result. "
    "All user-facing strings must be natural Japanese. "
    "Return concise JSON only."
)

FALLBACK_SCORE_RESULT = InterruptScoreResult(
    score=50,
    signal="yellow",
    confidence=25,
    headline="様子見のイエローです",
    reasons=["画像だけでは状況を読み切れません", "安全側に寄せて中間スコアにしました"],
    playfulSuggestion="5分後にもう一度だけ様子をうかがいましょう。",
    caution="これはジョーク判定です。重要な判断には使わないでください。",
)

NO_FACE_HEADLINE = "顔が見えないので赤です"
NO_FACE_REASONS = ["顔が映っていません", "表情が読めないので赤判定にしました"]
NO_FACE_SUGGESTION = "顔が見える場面で、もう一度だけ見てみましょう。"
SMILE_HEADLINE = "笑顔なので青です"
SMILE_REASONS = ["笑顔が見えます", "表情がやわらかく見えます"]
SMILE_SUGGESTION = "今なら軽く話しかけてみましょう。"
JUDGMENT_LEVEL_INSTRUCTIONS: dict[JudgmentLevel, str] = {
    "strict": (
        "Use a cautious threshold. "
        "If the person looks even slightly busy, concentrated, or hard to read, lean red or yellow."
    ),
    "balanced": (
        "Use a balanced threshold. "
        "If the scene is mixed, prefer yellow before jumping to red."
    ),
    "lenient": (
        "Use a friendly and permissive threshold. "
        "If the face is visible and there is no strong sign of interruption risk, lean yellow or blue."
    ),
}
JUDGMENT_LEVEL_SCORE_BIAS: dict[JudgmentLevel, int] = {
    "strict": -12,
    "balanced": 0,
    "lenient": 12,
}


def _extract_text_json(payload: dict[str, Any]) -> str | None:
    output_text = payload.get("output_text")
    if output_text:
        return str(output_text)

    try:
        for output in payload.get("output", []):
            for content in output.get("content", []):
                if content.get("type") == "output_text":
                    text = content.get("text")
                    if text:
                        return str(text)
    except Exception:
        return None

    return None


def _signal_from_score(score: int) -> str:
    if score <= 24:
        return "red"
    if score <= 59:
        return "yellow"
    return "blue"


def _score_to_legacy_visual(result: InterruptScoreResult) -> OpenAIVisionResult:
    visual_busy_score = max(0, min(100, 100 - result.score))
    confidence = max(0.0, min(1.0, result.confidence / 100))
    return OpenAIVisionResult(
        visual_busy_score=visual_busy_score,
        confidence=confidence,
        reasons=result.reasons,
        caution=result.caution,
    )


def _clamp_score(score: int) -> int:
    return max(0, min(100, score))


def _apply_judgment_level(score: int, judgment_level: JudgmentLevel) -> int:
    return _clamp_score(score + JUDGMENT_LEVEL_SCORE_BIAS[judgment_level])


def _apply_visibility_rules(parsed: dict[str, Any], judgment_level: JudgmentLevel = "balanced") -> dict[str, Any]:
    normalized = dict(parsed)
    score = int(normalized["score"])
    face_visible = bool(normalized.pop("faceVisible", True))
    smiling = bool(normalized.pop("smiling", False))

    if not face_visible:
        normalized["score"] = min(score, 15)
        normalized["signal"] = "red"
        normalized["headline"] = NO_FACE_HEADLINE
        normalized["reasons"] = NO_FACE_REASONS
        normalized["playfulSuggestion"] = NO_FACE_SUGGESTION
        return normalized

    if smiling:
        normalized["score"] = max(score, 75)
        normalized["signal"] = "blue"
        normalized["headline"] = SMILE_HEADLINE
        normalized["reasons"] = SMILE_REASONS
        normalized["playfulSuggestion"] = SMILE_SUGGESTION
        return normalized

    normalized["score"] = _apply_judgment_level(score, judgment_level)
    return normalized


async def score_interruptability(
    image_data_url: str,
    source_label: str = "unknown",
    judgment_level: JudgmentLevel = "balanced",
) -> InterruptScoreResult:
    if not settings.openai_api_key:
        return FALLBACK_SCORE_RESULT

    request_body = {
        "model": settings.openai_model,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            f"Input source: {source_label}. "
                            f"Judgment level: {judgment_level}. "
                            "Score from 0 to 100, where 0 means definitely do not interrupt and "
                            "100 means probably safe to chat. "
                            "Map to red (0-24), yellow (25-59), blue (60-100). "
                            "If the person is smiling, even softly, set smiling=true and return blue. "
                            "If no face is visible, set faceVisible=false and return red with a low score. "
                            f"{JUDGMENT_LEVEL_INSTRUCTIONS[judgment_level]} "
                            "Always decide faceVisible and smiling first from the image. "
                            "Give a short headline, exactly 2 short reasons based on visible evidence, "
                            "and one playful suggestion. "
                            "Write headline, reasons, playfulSuggestion, and caution in Japanese."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": image_data_url,
                        "detail": "low",
                    },
                ],
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "interrupt_score",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "score": {"type": "integer", "minimum": 0, "maximum": 100},
                        "signal": {"type": "string", "enum": ["red", "yellow", "blue"]},
                        "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
                        "faceVisible": {"type": "boolean"},
                        "smiling": {"type": "boolean"},
                        "headline": {"type": "string"},
                        "reasons": {
                            "type": "array",
                            "minItems": 2,
                            "maxItems": 2,
                            "items": {"type": "string"},
                        },
                        "playfulSuggestion": {"type": "string"},
                        "caution": {"type": "string"},
                    },
                    "required": [
                        "score",
                        "signal",
                        "confidence",
                        "faceVisible",
                        "smiling",
                        "headline",
                        "reasons",
                        "playfulSuggestion",
                        "caution",
                    ],
                },
            }
        },
    }

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }

    for _ in range(2):
        try:
            async with httpx.AsyncClient(timeout=settings.openai_timeout_sec) as client:
                response = await client.post(
                    "https://api.openai.com/v1/responses",
                    headers=headers,
                    json=request_body,
                )
                response.raise_for_status()

            payload = response.json()
            text_json = _extract_text_json(payload)
            if not text_json:
                continue

            parsed = _apply_visibility_rules(json.loads(text_json), judgment_level)
            result = InterruptScoreResult.model_validate(parsed)
            if result.signal != _signal_from_score(result.score):
                parsed["signal"] = _signal_from_score(int(parsed["score"]))
                result = InterruptScoreResult.model_validate(parsed)
            return result
        except (httpx.HTTPError, json.JSONDecodeError, ValidationError, KeyError, TypeError):
            continue

    return FALLBACK_SCORE_RESULT


async def analyze_visual_busy(image_base64: str) -> OpenAIVisionResult:
    result = await score_interruptability(f"data:image/jpeg;base64,{image_base64}", "legacy-camera-frame")
    return _score_to_legacy_visual(result)
