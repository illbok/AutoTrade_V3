"""Event name and stream helpers."""

from __future__ import annotations

from enum import Enum

from autotrade.core.config import settings


class EventName(str, Enum):
    """Enumerates canonical event identifiers for the platform."""

    MARKET_CANDLE_INGESTED = "market.candle.ingested"
    STRATEGY_SIGNAL_CREATED = "strategy.signal.created"
    POSITION_OPEN_REQUESTED = "position.open.requested"
    POSITION_OPEN_FILLED = "position.open.filled"
    POSITION_OPEN_FAILED = "position.open.failed"
    POSITION_CLOSE_REQUESTED = "position.close.requested"
    POSITION_CLOSE_FILLED = "position.close.filled"
    POSITION_CLOSE_FAILED = "position.close.failed"
    RISK_LIMIT_BREACHED = "risk.limit.breached"
    AI_PARAM_UPDATE_PROPOSED = "ai.param.update.proposed"
    AI_PARAM_UPDATE_APPLIED = "ai.param.update.applied"


STREAM_DEFINITIONS: dict[EventName, str] = {
    EventName.MARKET_CANDLE_INGESTED: "market.candles",
    EventName.STRATEGY_SIGNAL_CREATED: "strategy.signals",
    EventName.POSITION_OPEN_REQUESTED: "positions.lifecycle",
    EventName.POSITION_OPEN_FILLED: "positions.lifecycle",
    EventName.POSITION_OPEN_FAILED: "positions.lifecycle",
    EventName.POSITION_CLOSE_REQUESTED: "positions.lifecycle",
    EventName.POSITION_CLOSE_FILLED: "positions.lifecycle",
    EventName.POSITION_CLOSE_FAILED: "positions.lifecycle",
    EventName.RISK_LIMIT_BREACHED: "risk.alerts",
    EventName.AI_PARAM_UPDATE_PROPOSED: "ai.parameter_updates",
    EventName.AI_PARAM_UPDATE_APPLIED: "ai.parameter_updates",
}


def resolve_stream_name(event: EventName) -> str:
    """Return the fully-qualified stream name for ``event`` using settings."""

    base_stream = STREAM_DEFINITIONS[event]
    return settings.namespaced_stream(base_stream)

