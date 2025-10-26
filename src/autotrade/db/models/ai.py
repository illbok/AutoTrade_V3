"""AI and experimentation tables."""

from __future__ import annotations

from datetime import datetime

try:  # pragma: no cover - optional dependency import
    from sqlalchemy import DateTime, ForeignKey, String
    from sqlalchemy.dialects.postgresql import JSONB
    from sqlalchemy.orm import Mapped, mapped_column, relationship
except ModuleNotFoundError:  # pragma: no cover - fallback for tests
    from autotrade.db._compat_sqlalchemy import (  # type: ignore
        DateTime,
        ForeignKey,
        JSONB,
        Mapped,
        String,
        mapped_column,
        relationship,
    )

from autotrade.db.base import Base, TimestampMixin
from autotrade.db.models.strategy import Strategy


class Experiment(TimestampMixin, Base):
    """Tracks strategy parameter experiments and outcomes."""

    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    strategy_id: Mapped[int | None] = mapped_column(
        ForeignKey("strategies.id"), nullable=True
    )
    target: Mapped[str] = mapped_column(String(32), nullable=False)
    old_params: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict)
    new_params: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    result: Mapped[str | None] = mapped_column(String(64), nullable=True)

    strategy: Mapped[Strategy | None] = relationship(backref="experiments")


__all__ = ["Experiment"]
