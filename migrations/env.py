"""Alembic environment integrating with application settings."""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine

from autotrade.core.config import get_settings
from autotrade.db.base import metadata
import autotrade.db.models  # noqa: F401 - ensure model registration


config = context.config

if config.config_file_name is not None:  # pragma: no cover - configuration side effect
    fileConfig(config.config_file_name)


def get_url() -> str:
    """Resolve the database URL from application settings."""

    return get_settings().sqlalchemy_database_uri


target_metadata = metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""

    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(  # type: ignore[arg-type]
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    if isinstance(connectable, AsyncEngine):
        async def do_run_migrations() -> None:
            async with connectable.connect() as connection:
                await connection.run_sync(run_migrations)

        asyncio.run(do_run_migrations())
    else:
        with connectable.connect() as connection:
            run_migrations(connection)


def run_migrations(connection) -> None:
    """Helper to run migrations with a provided connection."""

    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():  # pragma: no cover - integration hook
    run_migrations_offline()
else:  # pragma: no cover - integration hook
    run_migrations_online()
