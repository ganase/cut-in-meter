from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = "Cut-in-Meter"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
    openai_timeout_sec: int = int(os.getenv("OPENAI_TIMEOUT_SEC", "30"))

    frame_interval_sec: int = int(os.getenv("FRAME_INTERVAL_SEC", "5"))
    image_max_width: int = int(os.getenv("IMAGE_MAX_WIDTH", "1024"))
    image_jpeg_quality: float = float(os.getenv("IMAGE_JPEG_QUALITY", "0.75"))


settings = Settings()
