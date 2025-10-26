"""Compatibility helpers for optional third-party dependencies.

The project uses Pydantic and pydantic-settings for configuration and schema
management. When those packages are unavailable (e.g. in constrained CI
sandboxes) we provide light-weight shims so that the rest of the codebase
continues to function. The shims are intentionally minimal and only implement
features currently exercised within the repository.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict


try:  # pragma: no cover - executed only when real dependency exists
    from pydantic import BaseModel, Field, model_validator  # type: ignore
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

    @dataclass
    class _FieldInfo:  # type: ignore
        default: Any = None
        alias: str | None = None
        name: str = ""

        def __set_name__(self, owner: type, name: str) -> None:
            self.name = name
            aliases = getattr(owner, "__field_aliases__", {})
            defaults = getattr(owner, "__field_defaults__", {})
            if self.alias:
                aliases[name] = self.alias
                owner.__field_aliases__ = aliases
            defaults[name] = self.default
            owner.__field_defaults__ = defaults

        def __get__(self, instance: Any, owner: type | None = None) -> Any:
            if instance is None:
                return self.default
            return instance.__dict__.get(self.name, self.default)

        def __set__(self, instance: Any, value: Any) -> None:
            instance.__dict__[self.name] = value

    def Field(default: Any = None, **kwargs: Any) -> Any:  # type: ignore
        alias = kwargs.get("validation_alias") or kwargs.get("alias")
        return _FieldInfo(default=default, alias=alias)

    def model_validator(*args: Any, **kwargs: Any):  # type: ignore
        def decorator(func: Any) -> Any:
            return func

        return decorator


try:  # pragma: no cover - executed only when real dependency exists
    from pydantic_settings import BaseSettings  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - simplified shim used in tests
    class BaseSettings:  # type: ignore
        """Simple environment-backed configuration container."""

        model_config: Dict[str, Any] = {}

        def __init__(self, **values: Any) -> None:
            annotations = getattr(self, "__annotations__", {})
            aliases = getattr(self, "__field_aliases__", {})
            defaults = getattr(self, "__field_defaults__", {})
            for name in annotations:
                default = values.get(name, defaults.get(name, getattr(self, name, None)))
                env_keys = [aliases.get(name), name.upper()]
                raw_value = default
                for key in env_keys:
                    if key and key in os.environ:
                        raw_value = os.getenv(key, default)
                        break
                value = self._coerce(raw_value, type(default))
                setattr(self, name, value)

        @staticmethod
        def _coerce(value: Any, target_type: type | None) -> Any:
            if target_type is None or value is None:
                return value
            if target_type is bool and isinstance(value, str):
                return value.lower() in {"1", "true", "yes", "on"}
            return value

