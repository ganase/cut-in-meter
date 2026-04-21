from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.routes.health import router as health_router
from app.routes.camera import router as camera_router


app = FastAPI(title=settings.app_name)

app.include_router(health_router)
app.include_router(camera_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def root() -> FileResponse:
    return FileResponse("app/static/index.html")
