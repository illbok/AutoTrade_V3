"""Compatibility helpers for optional third-party dependencies.

The project uses Pydantic and pydantic-settings for configuration and schema
management. When those packages are unavailable (e.g. in constrained CI
sandboxes) we provide light-weight shims so that the rest of the codebase
continues to function. The shims are intentionally minimal and only implement
features currently exercised within the repository.
"""

from __future__ import annotations

import os
from typing import Any, Dict


try:  # pragma: no cover - executed only when real dependency exists
    from pydantic import BaseModel, Field  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - simplified shim used in tests
    class BaseModel:  # type: ignore
        """Very small subset of :class:`pydantic.BaseModel`."""

        def __init__(self, **data: Any) -> None:
            for name in getattr(self, "__annotations__", {}):
                value = data.get(name, getattr(self, name, None))
                setattr(self, name, value)

        def model_dump(self) -> Dict[str, Any]:
            return {
                name: getattr(self, name)
                for name in getattr(self, "__annotations__", {})
            }

    def Field(default: Any = None, **_: Any) -> Any:  # type: ignore
        return default


try:  # pragma: no cover - executed only when real dependency exists
    from pydantic_settings import BaseSettings  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - simplified shim used in tests
    class BaseSettings:  # type: ignore
        """Simple environment-backed configuration container."""

        model_config: Dict[str, Any] = {}

        def __init__(self, **values: Any) -> None:
            annotations = getattr(self, "__annotations__", {})
            for name in annotations:
                default = values.get(name, getattr(self, name, None))
                env_key = name.upper()
                raw_value = os.getenv(env_key, default)
                value = self._coerce(raw_value, type(default))
                setattr(self, name, value)

        @staticmethod
        def _coerce(value: Any, target_type: type | None) -> Any:
            if target_type is None or value is None:
                return value
            if target_type is bool and isinstance(value, str):
                return value.lower() in {"1", "true", "yes", "on"}
            return value

