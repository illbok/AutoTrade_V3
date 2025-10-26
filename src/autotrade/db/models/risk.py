"""Risk monitoring tables."""

from __future__ import annotations

from datetime import datetime

try:  # pragma: no cover - optional dependency import
    from sqlalchemy import DateTime, Numeric, String
    from sqlalchemy.dialects.postgresql import JSONB
    from sqlalchemy.orm import Mapped, mapped_column
except ModuleNotFoundError:  # pragma: no cover - fallback for tests
    from autotrade.db._compat_sqlalchemy import (  # type: ignore
        DateTime,
        JSONB,
        Mapped,
        Numeric,
        String,
        mapped_column,
    )

from autotrade.db.base import Base, TimestampMixin


class RiskSnapshot(TimestampMixin, Base):
    """Periodic snapshot of system risk metrics."""

    __tablename__ = "risk_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    equity: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)
    exposure: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)
    value_at_risk: Mapped[float | None] = mapped_column(Numeric(20, 8), nullable=True)
    drawdown: Mapped[float | None] = mapped_column(Numeric(20, 8), nullable=True)
    limits: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict)


class RiskLimitBreach(TimestampMixin, Base):
    """Records of enforced risk limits."""

    __tablename__ = "risk_limit_breaches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    limit_type: Mapped[str] = mapped_column(String(32), index=True)
    current_value: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)
    threshold: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)
    action_taken: Mapped[str] = mapped_column(String(64), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


__all__ = ["RiskLimitBreach", "RiskSnapshot"]
