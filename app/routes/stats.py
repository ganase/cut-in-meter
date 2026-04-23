from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter

from app.services.data_service import read_csv

router = APIRouter(tags=["stats"])


@router.get("/api/stats")
async def get_stats(date: str | None = None) -> dict:
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    records = read_csv(date)
    return {"date": date, "records": records}


@router.get("/api/stats/minute")
async def get_minute_stats(date: str | None = None) -> dict:
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    records = read_csv(date)

    buckets: dict[str, list[float]] = defaultdict(list)
    for rec in records:
        try:
            ts = datetime.fromisoformat(rec["timestamp"])
            minute_key = ts.strftime("%H:%M")
            buckets[minute_key].append(float(rec["score"]))
        except (KeyError, ValueError):
            continue

    minute_data = [
        {"minute": k, "avgScore": round(sum(v) / len(v), 1), "count": len(v)}
        for k, v in sorted(buckets.items())
    ]
    return {"date": date, "minuteData": minute_data}
