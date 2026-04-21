from app.schemas import InterruptScoreResult, OpenAIVisionResult


def test_openai_schema_validation() -> None:
    valid = OpenAIVisionResult.model_validate(
        {
            "visual_busy_score": 55,
            "confidence": 0.7,
            "reasons": ["モニター注視", "入力中"],
            "caution": "過信しないでください",
        }
    )
    assert valid.visual_busy_score == 55


def test_interrupt_score_schema_validation() -> None:
    valid = InterruptScoreResult.model_validate(
        {
            "score": 72,
            "signal": "blue",
            "confidence": 81,
            "headline": "今なら比較的いけそうです",
            "reasons": ["姿勢が落ち着いて見える", "差し迫った作業中には見えません"],
            "playfulSuggestion": "コーヒー片手に一言だけ試してみましょう。",
            "caution": "これはジョーク判定です。",
        }
    )
    assert valid.score == 72
