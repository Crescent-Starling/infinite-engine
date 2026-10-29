"""Process liveness only: health is not a claim of knowledge-system readiness."""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from infinite_engine.config import Settings


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["infinite-engine"] = "infinite-engine"


def create_app(settings: Settings | None = None) -> FastAPI:
    app = FastAPI(title="Infinite Engine", version="0.1.0")
    app.state.settings = settings if settings is not None else Settings()

    @app.get("/api/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse()

    return app
