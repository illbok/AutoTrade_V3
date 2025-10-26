"""Declarative model registry."""

from autotrade.db.models.ai import Experiment
from autotrade.db.models.market import Candle, Tick
from autotrade.db.models.risk import RiskLimitBreach, RiskSnapshot
from autotrade.db.models.strategy import Signal, SignalSide, Strategy
from autotrade.db.models.trading import (
    Order,
    OrderStatus,
    Position,
    PositionSide,
    PositionStatus,
)

__all__ = [
    "Candle",
    "Experiment",
    "Order",
    "OrderStatus",
    "Position",
    "PositionSide",
    "PositionStatus",
    "RiskLimitBreach",
    "RiskSnapshot",
    "Signal",
    "SignalSide",
    "Strategy",
    "Tick",
]
