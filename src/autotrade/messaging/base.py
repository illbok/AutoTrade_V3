"""Protocol definitions shared by message bus implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from .envelope import EventEnvelope


@dataclass(slots=True)
class StreamMessage:
    """Canonical representation of a message consumed from the bus."""

    stream: str
    message_id: str
    data: Mapping[str, Any]


class EventBusProtocol(Protocol):
    """Interface implemented by message bus adapters."""

    async def publish(
        self, stream: str, data: Mapping[str, Any] | EventEnvelope
    ) -> str:
        """Publish ``data`` to ``stream`` returning the Redis message id."""

    async def create_consumer_group(
        self, stream: str, group: str, *, mkstream: bool = True, id: str = "$"
    ) -> None:
        """Create a consumer group for ``stream`` if it does not yet exist."""

    async def read(
        self,
        streams: Mapping[str, str],
        *,
        count: int = 1,
        block: int | None = None,
    ) -> Sequence[StreamMessage]:
        """Read messages from streams using the provided offsets."""

    async def read_group(
        self,
        group: str,
        consumer: str,
        streams: Mapping[str, str],
        *,
        count: int = 1,
        block: int | None = None,
    ) -> Sequence[StreamMessage]:
        """Read messages using a consumer group starting from ``streams`` offsets."""

    async def acknowledge(
        self, stream: str, group: str, message_ids: Sequence[str]
    ) -> int:
        """Acknowledge messages consumed through a consumer group."""

