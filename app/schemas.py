from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    model: str | None = None
    has_api_key: bool = False


class AnalyzeFrameRequest(BaseModel):
    source_user: str = "me"
    captured_at: datetime
    image_base64: str = Field(min_length=10)


class ScoreRequest(BaseModel):
    image_data_url: str = Field(min_length=20, alias="imageDataUrl")
    source_label: str = Field(default="unknown", alias="sourceLabel")


class InterruptScoreResult(BaseModel):
    score: int = Field(ge=0, le=100)
    signal: Literal["red", "yellow", "blue"]
    confidence: int = Field(ge=0, le=100)
    headline: str
    reasons: list[str] = Field(min_length=2, max_length=2)
    playful_suggestion: str = Field(alias="playfulSuggestion")
    caution: str


class ScoreResponse(InterruptScoreResult):
    model: str
    source_label: str = Field(alias="sourceLabel")
    generated_at: datetime = Field(alias="generatedAt")


class AnalyzeFrameResponse(BaseModel):
    source_user: str
    captured_at: datetime
    visual_busy_score: int
    talk_ok_score: int
    confidence: float
    reasons: list[str]
    comment: str
    disclaimer: str


class OpenAIVisionResult(BaseModel):
    visual_busy_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    caution: str


class ErrorPayload(BaseModel):
    error: str
    detail: dict[str, Any] | None = None
