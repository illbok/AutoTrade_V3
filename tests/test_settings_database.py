"""Tests for database-related configuration assembly."""

from __future__ import annotations

from importlib import reload

import pytest

from autotrade.core import config as config_module


@pytest.fixture(autouse=True)
def _reset_settings_cache(monkeypatch):
    """Clear cached settings between tests to apply env overrides."""

    config_module.get_settings.cache_clear()
    yield
    config_module.get_settings.cache_clear()


def test_database_url_is_assembled(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_USER", "tester")
    monkeypatch.setenv("DB_PASSWORD", "secret")
    monkeypatch.setenv("DB_HOST", "db.local")
    monkeypatch.setenv("DB_PORT", "5433")
    monkeypatch.setenv("DB_NAME", "autotrade_test")

    reload(config_module)
    settings = config_module.get_settings()

    assert (
        settings.sqlalchemy_database_uri
        == "postgresql+asyncpg://tester:secret@db.local:5433/autotrade_test"
    )


def test_redis_defaults_fallback(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.delenv("REDIS_SSL", raising=False)
    monkeypatch.delenv("REDIS_DB", raising=False)

    reload(config_module)
    settings = config_module.get_settings()

    kwargs = settings.redis_connection_kwargs
    assert kwargs["url"] == "redis://localhost:6379"
    assert "db" not in kwargs
