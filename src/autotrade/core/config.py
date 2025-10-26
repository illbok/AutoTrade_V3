"""Application configuration module.

Defines :class:`Settings` which centralizes runtime configuration loaded from
environment variables. The configuration follows the requirements captured in
``PLAN.md`` for the AutoTrade V3 system and establishes defaults suitable for
local development.
"""

from functools import lru_cache
from typing import Literal

from autotrade.core.compat import BaseSettings, Field, model_validator


class Settings(BaseSettings):
    """Base application settings loaded from environment variables.

    Attributes
    ----------
    environment:
        Deployment environment identifier. Determines default logging level and
        enables environment specific switches.
    app_name:
        Human friendly name used for application metadata, tracing and logging
        scopes.
    timezone:
        Canonical timezone identifier used by the shared clock utility.
    service_region:
        Human readable region label. Helps observability dashboards and alerts.
    enable_tracing:
        Feature flag that toggles OpenTelemetry instrumentation.
    database_scheme:
        SQLAlchemy compatible driver prefix. Defaults to the asyncpg dialect for
        PostgreSQL/TimescaleDB.
    database_user / database_password / database_host / database_port /
    database_name:
        Components used to assemble ``database_url`` when an explicit URL is not
        provided.
    database_url:
        Full SQLAlchemy connection URL. May be omitted when individual
        components are configured.
    database_echo:
        Toggles SQLAlchemy engine echo for debugging.
    redis_url:
        Connection string for Redis cache/event bus.
    redis_ssl:
        Enables SSL/TLS for Redis connections.
    redis_db:
        Optional logical database selection for Redis.
    """

    environment: Literal["local", "development", "staging", "production"] = Field(
        default="local", validation_alias="APP_ENV"
    )
    app_name: str = Field(default="AutoTrade V3", validation_alias="APP_NAME")
    timezone: str = Field(default="Asia/Seoul", validation_alias="APP_TIMEZONE")
    service_region: str = Field(
        default="ap-northeast-2", validation_alias="APP_SERVICE_REGION"
    )
    enable_tracing: bool = Field(
        default=True, validation_alias="APP_ENABLE_TRACING"
    )
    database_scheme: Literal["postgresql+asyncpg"] = Field(
        default="postgresql+asyncpg", validation_alias="DB_SCHEME"
    )
    database_user: str = Field(default="autotrade", validation_alias="DB_USER")
    database_password: str = Field(
        default="autotrade", validation_alias="DB_PASSWORD"
    )
    database_host: str = Field(default="localhost", validation_alias="DB_HOST")
    database_port: int = Field(default=5432, validation_alias="DB_PORT")
    database_name: str = Field(default="autotrade", validation_alias="DB_NAME")
    database_url: str | None = Field(
        default=None,
        validation_alias="DATABASE_URL",
    )
    database_echo: bool = Field(default=False, validation_alias="DB_ECHO")
    redis_url: str | None = Field(
        default=None,
        validation_alias="REDIS_URL",
    )
    redis_host: str = Field(default="localhost", validation_alias="REDIS_HOST")
    redis_port: int = Field(default=6379, validation_alias="REDIS_PORT")
    redis_ssl: bool = Field(default=False, validation_alias="REDIS_SSL")
    redis_db: int | None = Field(default=None, validation_alias="REDIS_DB")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        """Construct ``database_url`` when only components are provided."""

        self.database_url = self._ensure_database_url()
        return self

    def _ensure_database_url(self) -> str:
        if self.database_url:
            return str(self.database_url)
        return (
            f"{self.database_scheme}://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @property
    def sqlalchemy_database_uri(self) -> str:
        """Return the SQLAlchemy compatible database URI."""

        return self._ensure_database_url()

    @property
    def redis_connection_kwargs(self) -> dict[str, object]:
        """Return keyword arguments for Redis client construction."""

        kwargs: dict[str, object] = {}
        if self.redis_url:
            kwargs["url"] = str(self.redis_url)
        else:
            scheme = "rediss" if self.redis_ssl else "redis"
            kwargs["url"] = f"{scheme}://{self.redis_host}:{self.redis_port}"
        if self.redis_db is not None:
            kwargs["db"] = self.redis_db
        return kwargs


@lru_cache
def get_settings() -> Settings:
    """Return the cached :class:`Settings` instance."""

    return Settings()


settings = get_settings()
"""Module level settings singleton for convenience."""
