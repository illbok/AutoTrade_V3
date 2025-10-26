"""Validate that SQLAlchemy models are registered with shared metadata."""

from __future__ import annotations

import autotrade.db.models  # noqa: F401 - ensure import side-effects
from autotrade.db import metadata


def test_metadata_contains_expected_tables():
    expected_tables = {
        "candles",
        "ticks",
        "strategies",
        "signals",
        "positions",
        "orders",
        "risk_snapshots",
        "risk_limit_breaches",
        "experiments",
    }

    assert expected_tables.issubset(set(metadata.tables))
