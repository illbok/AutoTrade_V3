"""Order and position tables."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

try:  # pragma: no cover - optional dependency import
    from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Numeric, String
    from sqlalchemy.orm import Mapped, mapped_column, relationship
except ModuleNotFoundError:  # pragma: no cover - fallback for tests
    from autotrade.db._compat_sqlalchemy import (  # type: ignore
        DateTime,
        Enum as SAEnum,
        ForeignKey,
        Mapped,
        Numeric,
        String,
        mapped_column,
        relationship,
    )

from autotrade.db.base import Base, TimestampMixin
from autotrade.db.models.strategy import Signal


class PositionStatus(str, Enum):
    """Lifecycle stages for a trading position."""

    NEW = "new"
    OPEN = "open"
    PARTIAL = "partial"
    CLOSED = "closed"
    FAILED = "failed"


class OrderStatus(str, Enum):
    """Order execution states."""

    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PositionSide(str, Enum):
    """Side of the position relative to the base currency."""

    LONG = "long"
    SHORT = "short"


class Position(TimestampMixin, Base):
    """Represents a tracked trading position."""

    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    signal_id: Mapped[int | None] = mapped_column(ForeignKey("signals.id"), nullable=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    side: Mapped[PositionSide] = mapped_column(SAEnum(PositionSide), index=True)
    size: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    entry_avg: Mapped[float] = mapped_column(Numeric(18, 8), nullable=True)
    leverage: Mapped[float] = mapped_column(Numeric(6, 2), nullable=True)
    status: Mapped[PositionStatus] = mapped_column(SAEnum(PositionStatus), index=True)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    realized_pnl: Mapped[float | None] = mapped_column(Numeric(18, 8), nullable=True)
    max_drawdown: Mapped[float | None] = mapped_column(Numeric(18, 8), nullable=True)

    signal: Mapped[Signal | None] = relationship(backref="positions")
    orders: Mapped[list["Order"]] = relationship(back_populates="position")


class Order(TimestampMixin, Base):
    """Individual orders executed for a position."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    position_id: Mapped[int] = mapped_column(ForeignKey("positions.id"), index=True)
    exchange: Mapped[str] = mapped_column(String(16), nullable=False, default="upbit")
    order_type: Mapped[str] = mapped_column(String(16), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(18, 8), nullable=True)
    quantity: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), index=True)
    placed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    filled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    slippage: Mapped[float | None] = mapped_column(Numeric(18, 8), nullable=True)

    position: Mapped[Position] = relationship(back_populates="orders")


__all__ = [
    "Order",
    "OrderStatus",
    "Position",
    "PositionSide",
    "PositionStatus",
]
