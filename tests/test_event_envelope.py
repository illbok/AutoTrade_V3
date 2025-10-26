"""Tests for event envelope serialization."""

from __future__ import annotations

from datetime import datetime, timezone

from autotrade.core.schemas import CandlePayload
from autotrade.messaging import EventEnvelope, EventName


def test_event_envelope_serializes_payload_model():
    now = datetime.now(tz=timezone.utc)
    payload = CandlePayload(
        symbol="KRW-BTC",
        interval="1m",
        open=1.0,
        high=2.0,
        low=0.5,
        close=1.5,
        volume=10.0,
        timestamp_utc=now,
        timestamp_kst=now,
    )

    envelope = EventEnvelope(
        name=EventName.MARKET_CANDLE_INGESTED,
        producer="tests",
        produced_at_utc=now,
        produced_at_kst=now,
        payload=payload,
    )

    message = envelope.as_message()

    assert message["payload"]["symbol"] == "KRW-BTC"
    assert message["payload"]["source"] == "upbit"
