"""Market data related tables."""

from __future__ import annotations

from datetime import datetime

try:  # pragma: no cover - optional dependency import
    from sqlalchemy import DateTime, Float, String
    from sqlalchemy.orm import Mapped, mapped_column
except ModuleNotFoundError:  # pragma: no cover - fallback for tests
    from autotrade.db._compat_sqlalchemy import (  # type: ignore
        DateTime,
        Float,
        Mapped,
        String,
        mapped_column,
    )

from autotrade.db.base import Base, TimestampMixin


class Candle(TimestampMixin, Base):
    """Normalized candlestick data."""

    __tablename__ = "candles"

    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    interval: Mapped[str] = mapped_column(String(16), primary_key=True)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, index=True
    )
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="upbit")
    ingest_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )


class Tick(TimestampMixin, Base):
    """Optional tick level trade data."""

    __tablename__ = "ticks"

    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, index=True
    )
    price: Mapped[float] = mapped_column(Float, nullable=False)
    size: Mapped[float] = mapped_column(Float, nullable=False)


__all__ = ["Candle", "Tick"]
