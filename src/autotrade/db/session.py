"""Async SQLAlchemy engine and session helpers."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any

try:  # pragma: no cover - optional dependency import
    from sqlalchemy.ext.asyncio import (
        AsyncEngine,
        AsyncSession,
        async_sessionmaker,
        create_async_engine as _create_async_engine,
    )
except ModuleNotFoundError:  # pragma: no cover - fallback for tests
    AsyncEngine = Any  # type: ignore
    AsyncSession = Any  # type: ignore

    def async_sessionmaker(*args: Any, **kwargs: Any):  # type: ignore
        raise RuntimeError("SQLAlchemy is required for database sessions")

    def _create_async_engine(*args: Any, **kwargs: Any):  # type: ignore
        raise RuntimeError("SQLAlchemy is required for database sessions")

from autotrade.core.config import get_settings


def create_async_engine(engine_factory: Callable[[], str] | None = None) -> AsyncEngine:
    """Create an :class:`~sqlalchemy.ext.asyncio.AsyncEngine` instance.

    Parameters
    ----------
    engine_factory:
        Optional callable returning the database URI. Primarily useful for
        testing where configuration needs to be overridden.
    """

    settings = get_settings()
    database_uri = engine_factory() if engine_factory else settings.sqlalchemy_database_uri
    return _create_async_engine(database_uri, echo=settings.database_echo)


def get_async_session(engine: AsyncEngine | None = None) -> async_sessionmaker[AsyncSession]:
    """Return a configured :func:`async_sessionmaker`."""

    if engine is None:
        engine = create_async_engine()
    return async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def session_scope(session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
    """Provide a transactional scope for async database operations."""

    session = session_factory()
    try:
        yield session
        await session.commit()
    except Exception:  # pragma: no cover - protective rollback
        await session.rollback()
        raise
    finally:
        await session.close()


__all__ = ["create_async_engine", "get_async_session", "session_scope"]
