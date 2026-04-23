from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app.config import settings
from app.schemas import AnalyzeFrameRequest, AnalyzeFrameResponse, ScoreRequest, ScoreResponse
from app.services.data_service import append_record, new_record_id, save_snapshot
from app.services.openai_vision import analyze_visual_busy, score_interruptability

router = APIRouter(tags=["camera"])


@router.post("/api/score", response_model=ScoreResponse)
async def score_image(req: ScoreRequest) -> ScoreResponse:
    record_id = new_record_id()
    result = await score_interruptability(req.image_data_url, req.source_label, req.judgment_level)
    now_local = datetime.now()
    now_utc = datetime.now(timezone.utc)

    snapshot_filename = save_snapshot(req.image_data_url, req.device_name, now_local, record_id)
    append_record(
        record_id=record_id,
        timestamp=now_local,
        score=result.score,
        confidence=result.confidence,
        signal=result.signal,
        source_label=req.source_label,
        judgment_level=req.judgment_level,
        snapshot_filename=snapshot_filename,
    )

    return ScoreResponse(
        **result.model_dump(by_alias=True),
        recordId=record_id,
        model=settings.openai_model,
        sourceLabel=req.source_label,
        generatedAt=now_utc,
        judgmentLevel=req.judgment_level,
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
