"""FastAPI entrypoint providing shared system endpoints."""

from __future__ import annotations

from fastapi import FastAPI

from autotrade.core.clock import now
from autotrade.core.config import settings
from autotrade.core.logging import configure_logging

configure_logging()

app = FastAPI(title=settings.app_name)


@app.get("/health", tags=["system"])
def healthcheck() -> dict[str, object]:
    """Simple health endpoint exposing synchronized timestamps."""

    snapshot = now()
    return {
        "status": "ok",
        "environment": settings.environment,
        "timestamps": {
            "utc": snapshot.utc.isoformat(),
            "kst": snapshot.kst.isoformat(),
        },
    }


__all__ = ["app"]
