"""Tests covering event name utilities."""

from __future__ import annotations

from importlib import reload

import pytest

from autotrade.core import config as config_module
from autotrade.messaging import events as events_module


@pytest.fixture(autouse=True)
def _reset_settings(monkeypatch):
    """Reset cached settings and event module state between tests."""

    for var in ["MESSAGE_NAMESPACE"]:
        monkeypatch.delenv(var, raising=False)
    config_module.get_settings.cache_clear()
    reload(config_module)
    reload(events_module)
    yield
    config_module.get_settings.cache_clear()
    reload(config_module)
    reload(events_module)


def test_stream_definitions_cover_all_events():
    assert set(events_module.STREAM_DEFINITIONS) == set(events_module.EventName)


def test_resolve_stream_name_applies_namespace(monkeypatch):
    monkeypatch.setenv("MESSAGE_NAMESPACE", "autotrade.test")
    config_module.get_settings.cache_clear()
    reload(config_module)
    reload(events_module)

    stream = events_module.resolve_stream_name(
        events_module.EventName.MARKET_CANDLE_INGESTED
    )
    assert stream == "autotrade.test.market.candles"
