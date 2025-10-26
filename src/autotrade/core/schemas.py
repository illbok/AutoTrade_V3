"""Shared Pydantic models used across services."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from autotrade.core.compat import BaseModel, Field


class CandlePayload(BaseModel):
    """Canonical payload for ``market.candle.ingested`` events."""

    symbol: str
    interval: str
    open: float = Field(..., ge=0)
    high: float = Field(..., ge=0)
    low: float = Field(..., ge=0)
    close: float = Field(..., ge=0)
    volume: float = Field(..., ge=0)
    timestamp_utc: datetime
    timestamp_kst: datetime
    source: Literal["upbit"] = "upbit"


class StrategySignal(BaseModel):
    """Payload emitted by the strategy service."""

    strategy_id: str
    symbol: str
    side: Literal["buy", "sell"]
    entry_price: float = Field(..., gt=0)
    take_profit: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)
    confidence: float = Field(..., ge=0, le=1)
    parameters: dict
    created_at_utc: datetime
    created_at_kst: datetime


__all__ = ["CandlePayload", "StrategySignal"]
