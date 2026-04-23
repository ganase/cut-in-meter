from __future__ import annotations

import base64
import csv
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
SNAPSHOTS_DIR = DATA_DIR / "snapshots"

CSV_FIELDS = ["id", "timestamp", "score", "confidence", "signal", "source_label", "judgment_level", "snapshot_filename"]


def _ensure_dirs() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    SNAPSHOTS_DIR.mkdir(exist_ok=True)


def new_record_id() -> str:
    return str(uuid.uuid4())


def _csv_path(dt: datetime) -> Path:
    return DATA_DIR / f"{dt.strftime('%Y-%m-%d')}.csv"


def append_record(
    record_id: str,
    timestamp: datetime,
    score: int,
    confidence: int,
    signal: str,
    source_label: str,
    judgment_level: str,
    snapshot_filename: str,
) -> None:
    _ensure_dirs()
    path = _csv_path(timestamp)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "id": record_id,
            "timestamp": timestamp.isoformat(),
            "score": score,
            "confidence": confidence,
            "signal": signal,
            "source_label": source_label,
            "judgment_level": judgment_level,
            "snapshot_filename": snapshot_filename,
        })


def save_snapshot(image_data_url: str, device_name: str, timestamp: datetime, record_id: str) -> str:
    _ensure_dirs()
    _, _, encoded = image_data_url.partition(",")
    safe_device = "".join(c if (c.isalnum() or c in "-_") else "_" for c in device_name)[:40]
    ts_str = timestamp.strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_device}_{ts_str}_{record_id[:8]}.jpg"
    try:
        (SNAPSHOTS_DIR / filename).write_bytes(base64.b64decode(encoded))
    except Exception:
        return ""
    return filename


def read_csv(date_str: str) -> list[dict[str, str]]:
    path = DATA_DIR / f"{date_str}.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))
