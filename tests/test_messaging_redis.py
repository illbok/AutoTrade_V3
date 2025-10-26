"""Tests for the Redis event bus adapter."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from autotrade.messaging.redis import RedisEventBus, ResponseError
from autotrade.messaging.envelope import EventEnvelope
from autotrade.messaging.events import EventName
from autotrade.core.schemas import CandlePayload


def test_publish_serializes_and_returns_id():
    client = AsyncMock()
    client.xadd.return_value = b"1685695969-0"
    bus = RedisEventBus(client)

    result = asyncio.run(bus.publish("stream", {"foo": "bar"}))

    client.xadd.assert_awaited_once()
    assert result == "1685695969-0"


def test_read_decodes_json_payload():
    client = AsyncMock()
    client.xread.return_value = [
        (b"stream", [(b"1-0", {b"event": b"{\"foo\": \"bar\"}"})])
    ]
    bus = RedisEventBus(client)

    messages = asyncio.run(bus.read({"stream": "0"}))

    assert len(messages) == 1
    assert messages[0].stream == "stream"
    assert messages[0].message_id == "1-0"
    assert messages[0].data == {"foo": "bar"}


def test_read_group_uses_consumer_group():
    client = AsyncMock()
    client.xreadgroup.return_value = [
        (b"stream", [(b"2-0", {b"event": b"{\"foo\": \"baz\"}"})])
    ]
    bus = RedisEventBus(client)

    messages = asyncio.run(bus.read_group("group", "consumer", {"stream": ">"}))

    client.xreadgroup.assert_awaited_once_with(
        groupname="group",
        consumername="consumer",
        streams={"stream": ">"},
        count=1,
        block=None,
    )
    assert messages[0].message_id == "2-0"


def test_create_consumer_group_ignores_existing_group():
    client = AsyncMock()
    client.xgroup_create.side_effect = ResponseError("BUSYGROUP Consumer Group exists")
    bus = RedisEventBus(client)

    asyncio.run(bus.create_consumer_group("stream", "group"))

    client.xgroup_create.assert_awaited_once()


def test_acknowledge_forwards_to_client():
    client = AsyncMock()
    client.xack.return_value = 1
    bus = RedisEventBus(client)

    result = asyncio.run(bus.acknowledge("stream", "group", ["1-0"]))

    client.xack.assert_awaited_once_with("stream", "group", "1-0")
    assert result == 1


def test_publish_accepts_event_envelope():
    client = AsyncMock()
    client.xadd.return_value = "1-0"
    bus = RedisEventBus(client)

    now = datetime.now(tz=timezone.utc)
    payload = CandlePayload(
        symbol="KRW-BTC",
        interval="1m",
        open=1.0,
        high=1.5,
        low=0.8,
        close=1.2,
        volume=5.0,
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

    asyncio.run(bus.publish("stream", envelope))

    client.xadd.assert_awaited_once()
