"""Application wide logging helpers."""

from __future__ import annotations

import logging
from typing import Optional

from .config import settings


def configure_logging(level: Optional[int] = None) -> None:
    """Configure global logging.

    Parameters
    ----------
    level:
        Override logging level. When ``None`` the function derives an
        environment-aware level.
    """

    if level is None:
        if settings.environment in {"production", "staging"}:
            level = logging.INFO
        else:
            level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


__all__ = ["configure_logging"]
