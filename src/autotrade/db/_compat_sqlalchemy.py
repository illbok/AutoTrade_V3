"""Minimal SQLAlchemy compatibility layer for test environments.

This shim is intentionally lightweight. It only implements the subset of
SQLAlchemy's declarative API required by the unit tests so that the codebase can
be imported without the real dependency installed. The functionality is
restricted to metadata bookkeeping; no actual database interaction is
supported.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, Optional


class _Func:
    def now(self) -> Callable[[], datetime]:  # pragma: no cover - trivial shim
        return datetime.utcnow


func = _Func()


@dataclass
class Column:
    """Simple column descriptor capturing declaration arguments."""

    type_: Any = None
    kwargs: Dict[str, Any] = None  # type: ignore[assignment]

    def __init__(self, type_: Any = None, **kwargs: Any) -> None:
        self.type_ = type_
        self.kwargs = kwargs


def mapped_column(type_: Any = None, **kwargs: Any) -> Column:
    return Column(type_=type_, **kwargs)


class MetaData:
    def __init__(self, naming_convention: Optional[Dict[str, str]] = None) -> None:
        self.naming_convention = naming_convention or {}
        self.tables: Dict[str, Any] = {}


class DeclarativeMeta(type):
    def __init__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> None:
        super().__init__(name, bases, attrs)
        tablename = attrs.get("__tablename__")
        metadata = getattr(cls, "metadata", None)
        if tablename and metadata is not None:
            metadata.tables[tablename] = cls


class DeclarativeBase(metaclass=DeclarativeMeta):
    metadata = MetaData()


Mapped = Any


class DateTime:
    def __init__(self, timezone: bool = False) -> None:  # pragma: no cover - trivial shim
        self.timezone = timezone


class String:
    def __init__(self, length: int | None = None) -> None:
        self.length = length


class Float:
    pass


class Numeric:
    def __init__(self, precision: int, scale: int) -> None:
        self.precision = precision
        self.scale = scale


class Text:
    pass


class ForeignKey:
    def __init__(self, target: str) -> None:  # pragma: no cover - trivial shim
        self.target = target


class Enum:
    def __init__(self, enum_cls: Any) -> None:
        self.enum_cls = enum_cls


class JSONB:
    pass


def relationship(*args: Any, **kwargs: Any) -> None:  # pragma: no cover - simplified shim
    return None


class pool:  # pragma: no cover - used for Alembic configuration compatibility
    class NullPool:
        pass


def engine_from_config(*args: Any, **kwargs: Any):  # pragma: no cover - alembic shim
    raise RuntimeError("SQLAlchemy engine not available in compatibility mode")


class AsyncEngine:  # pragma: no cover - alembic shim
    pass


__all__ = [
    "AsyncEngine",
    "Column",
    "DateTime",
    "DeclarativeBase",
    "Enum",
    "Float",
    "ForeignKey",
    "JSONB",
    "Mapped",
    "MetaData",
    "Numeric",
    "String",
    "Text",
    "func",
    "mapped_column",
    "pool",
    "relationship",
]
