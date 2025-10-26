"""Pydantic models describing event envelopes."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from autotrade.core.compat import BaseModel, Field

from .events import EventName


class EventEnvelope(BaseModel):
    """Standard metadata wrapper around event payloads."""

    name: EventName
    version: str = Field(default="1.0.0")
    producer: str
    produced_at_utc: datetime
    produced_at_kst: datetime
    payload: Any
    correlation_id: str | None = None
    causation_id: str | None = None

    def payload_dict(self) -> dict[str, Any]:
        """Return the payload as a JSON-serialisable mapping."""

        payload = self.payload
        if hasattr(payload, "model_dump"):
            return payload.model_dump()
        if isinstance(payload, dict):
            return dict(payload)
        try:
            return dict(payload)
        except TypeError:
            raise TypeError("Event payload cannot be represented as a mapping") from None

    def as_message(self) -> dict[str, Any]:
        """Return a serialisable dictionary representation of the event."""

        return {
            "name": str(self.name.value if hasattr(self.name, "value") else self.name),
            "version": self.version,
            "producer": self.producer,
            "produced_at_utc": self.produced_at_utc,
            "produced_at_kst": self.produced_at_kst,
            "payload": self.payload_dict(),
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
        }

