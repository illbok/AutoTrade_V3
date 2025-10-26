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


class PositionLifecycleEvent(BaseModel):
    """Payload emitted when a position lifecycle event occurs."""

    position_id: str
    symbol: str
    action: Literal["open", "close"]
    status: Literal["requested", "filled", "failed"]
    side: Literal["buy", "sell"]
    quantity: float = Field(..., gt=0)
    price: float | None = Field(default=None, gt=0)
    leverage: float | None = Field(default=None, gt=0)
    reason: str | None = None
    timestamp_utc: datetime
    timestamp_kst: datetime


class RiskLimitBreach(BaseModel):
    """Payload describing a risk engine breach notification."""

    breach_type: str
    current_value: float
    limit_value: float
    unit: str
    action_taken: Literal["blocked", "reduced", "liquidated", "alerted"]
    snapshot_id: str | None = None
    timestamp_utc: datetime
    timestamp_kst: datetime


class AIParameterProposal(BaseModel):
    """Payload emitted when the AI service proposes parameter changes."""

    proposal_id: str
    target: str
    current_parameters: dict
    proposed_parameters: dict
    metric_snapshot: dict | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    proposed_at_utc: datetime
    proposed_at_kst: datetime


class AIParameterApplication(BaseModel):
    """Payload emitted when a proposal is applied."""

    proposal_id: str
    applied_by: str | None = None
    notes: str | None = None
    applied_at_utc: datetime
    applied_at_kst: datetime


__all__ = [
    "CandlePayload",
    "StrategySignal",
    "PositionLifecycleEvent",
    "RiskLimitBreach",
    "AIParameterProposal",
    "AIParameterApplication",
]
