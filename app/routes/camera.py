from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app.config import settings
from app.schemas import AnalyzeFrameRequest, AnalyzeFrameResponse, ScoreRequest, ScoreResponse
from app.services.openai_vision import analyze_visual_busy, score_interruptability

router = APIRouter(tags=["camera"])


@router.post("/api/score", response_model=ScoreResponse)
async def score_image(req: ScoreRequest) -> ScoreResponse:
    result = await score_interruptability(req.image_data_url, req.source_label)
    return ScoreResponse(
        **result.model_dump(by_alias=True),
        model=settings.openai_model,
        sourceLabel=req.source_label,
        generatedAt=datetime.now(timezone.utc),
    )


@router.post("/api/analyze/frame", response_model=AnalyzeFrameResponse)
async def analyze_frame(req: AnalyzeFrameRequest) -> AnalyzeFrameResponse:
    visual = await analyze_visual_busy(req.image_base64)
    talk_ok = max(0, min(100, 100 - visual.visual_busy_score))

    return AnalyzeFrameResponse(
        source_user=req.source_user,
        captured_at=req.captured_at,
        visual_busy_score=visual.visual_busy_score,
        talk_ok_score=talk_ok,
        confidence=visual.confidence,
        reasons=visual.reasons,
        comment="これは画像ベースだけのジョーク判定です。",
        disclaimer="これはジョーク判定です。真に受けないでください。",
    )
