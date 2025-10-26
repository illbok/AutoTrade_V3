"""Redis Streams backed event bus implementation."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Mapping, Sequence

try:  # pragma: no cover - exercised when redis is available
    from redis.asyncio import Redis  # type: ignore
    from redis.exceptions import ResponseError  # type: ignore
    _redis_missing: Exception | None = None
except ModuleNotFoundError:  # pragma: no cover - executed in minimal test envs
    Redis = Any  # type: ignore

    class ResponseError(Exception):  # type: ignore
        """Fallback exception used when redis-py is not installed."""

    _redis_missing = ModuleNotFoundError(
        "The 'redis' package is required for RedisEventBus operations."
    )

from autotrade.core.config import Settings, get_settings

from .base import EventBusProtocol, StreamMessage
from .envelope import EventEnvelope


def _serialize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Unsupported type {type(value)!r} for JSON serialization")


def _encode_message(data: Mapping[str, Any] | EventEnvelope) -> dict[str, str]:
    if isinstance(data, EventEnvelope):
        payload = data.as_message()
    else:
        payload = dict(data)
    return {"event": json.dumps(payload, default=_serialize)}


def _decode_message(fields: Mapping[bytes | str, bytes | str]) -> Mapping[str, Any]:
    event_field = fields.get(b"event") if b"event" in fields else fields.get("event")
    if event_field is None:
        return {
            (key.decode() if isinstance(key, bytes) else key): (
                value.decode() if isinstance(value, bytes) else value
            )
            for key, value in fields.items()
        }
    if isinstance(event_field, bytes):
        event_field = event_field.decode()
    return json.loads(event_field)


class RedisEventBus(EventBusProtocol):
    """Event bus backed by Redis Streams."""

    def __init__(self, client: Redis) -> None:
        self._client = client

    async def publish(
        self, stream: str, data: Mapping[str, Any] | EventEnvelope
    ) -> str:
        encoded = _encode_message(data)
        message_id = await self._client.xadd(stream, encoded)
        if isinstance(message_id, bytes):
            return message_id.decode()
        return str(message_id)

    async def create_consumer_group(
        self, stream: str, group: str, *, mkstream: bool = True, id: str = "$"
    ) -> None:
        try:
            await self._client.xgroup_create(stream, group, id=id, mkstream=mkstream)
        except ResponseError as exc:  # pragma: no cover - defensive branch
            if "BUSYGROUP" not in str(exc):
                raise

    async def read(
        self,
        streams: Mapping[str, str],
        *,
        count: int = 1,
        block: int | None = None,
    ) -> Sequence[StreamMessage]:
        response = await self._client.xread(streams=streams, count=count, block=block)
        return self._format_stream_response(response)

    async def read_group(
        self,
        group: str,
        consumer: str,
        streams: Mapping[str, str],
        *,
        count: int = 1,
        block: int | None = None,
    ) -> Sequence[StreamMessage]:
        response = await self._client.xreadgroup(
            groupname=group,
            consumername=consumer,
            streams=streams,
            count=count,
            block=block,
        )
        return self._format_stream_response(response)

    async def acknowledge(
        self, stream: str, group: str, message_ids: Sequence[str]
    ) -> int:
        return await self._client.xack(stream, group, *message_ids)

    def _format_stream_response(self, response: Any) -> Sequence[StreamMessage]:
        messages: list[StreamMessage] = []
        if not response:
            return messages
        for stream_name, entries in response:
            stream_str = stream_name.decode() if isinstance(stream_name, bytes) else stream_name
            for message_id, fields in entries:
                message_id_str = (
                    message_id.decode() if isinstance(message_id, bytes) else message_id
                )
                payload = _decode_message(fields)
                messages.append(
                    StreamMessage(stream=str(stream_str), message_id=str(message_id_str), data=payload)
                )
        return messages


def build_redis_bus(config: Settings | None = None) -> RedisEventBus:
    """Instantiate a :class:`RedisEventBus` using application settings."""

    if _redis_missing is not None:  # pragma: no cover - requires redis package
        raise _redis_missing
    cfg = config or get_settings()
    client = Redis(**cfg.redis_connection_kwargs)
    return RedisEventBus(client)


__all__ = ["RedisEventBus", "build_redis_bus", "ResponseError"]

