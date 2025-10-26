"""Shared SQLAlchemy declarative base and mixins."""

from __future__ import annotations

from datetime import datetime, timezone

try:  # pragma: no cover - import depends on optional dependency
    from sqlalchemy import DateTime, MetaData, func
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
except ModuleNotFoundError:  # pragma: no cover - fallback used during tests
    from autotrade.db._compat_sqlalchemy import (  # type: ignore
        DateTime,
        DeclarativeBase,
        Mapped,
        MetaData,
        func,
        mapped_column,
    )

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Base(DeclarativeBase):
    """Declarative base class configured with project metadata."""

    metadata = metadata


class TimestampMixin:
    """Common timestamp columns for audit purposes."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


__all__ = ["Base", "TimestampMixin", "metadata"]
