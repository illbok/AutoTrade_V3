"""Application configuration module.

Defines :class:`Settings` which centralizes runtime configuration loaded from
environment variables. The configuration follows the requirements captured in
``PLAN.md`` for the AutoTrade V3 system and establishes defaults suitable for
local development.
"""

from functools import lru_cache
from typing import Literal

from autotrade.core.compat import BaseSettings, Field


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

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Settings:
    """Return the cached :class:`Settings` instance."""

    return Settings()


settings = get_settings()
"""Module level settings singleton for convenience."""
