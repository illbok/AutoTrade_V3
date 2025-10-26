"""Shared clock utilities ensuring synchronized timestamps across services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from .config import settings


@dataclass(frozen=True, slots=True)
class TimeSnapshot:
    """Container for paired UTC and KST timestamps."""

    utc: datetime
    kst: datetime


def now() -> TimeSnapshot:
    """Return the current time in both UTC and KST.

    The reference clock pulls UTC time first to avoid drift, then converts the
    timestamp to the configured canonical timezone (defaulting to Asia/Seoul).
    All timestamps are timezone-aware ``datetime`` objects.
    """

    utc_time = datetime.now(tz=timezone.utc)
    kst_zone = ZoneInfo(settings.timezone)
    return TimeSnapshot(utc=utc_time, kst=utc_time.astimezone(kst_zone))


__all__ = ["TimeSnapshot", "now"]
