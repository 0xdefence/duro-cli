from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    INFRA_FAILED = "infra_failed"
    PROVIDER_ERROR = "provider_error"
    CONFIG_ERROR = "config_error"
    SCHEMA_ERROR = "schema_error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class DuroError:
    code: ErrorCode
    message: str
    details: dict[str, Any] | None = None


def required_env_for_provider(provider: str) -> list[str]:
    p = (provider or "").lower().strip()
    if p == "openai":
        return ["OPENAI_API_KEY"]
    if p == "anthropic":
        return ["ANTHROPIC_API_KEY"]
    if p == "gemini":
        return ["GEMINI_API_KEY"]
    if p == "openrouter":
        return ["OPENROUTER_API_KEY"]
    # mock/ollama/local typically no mandatory key
    return []


def validate_provider_config(provider: str, env: dict[str, str]) -> list[DuroError]:
    errs: list[DuroError] = []
    req = required_env_for_provider(provider)
    for key in req:
        if not env.get(key):
            errs.append(
                DuroError(
                    code=ErrorCode.CONFIG_ERROR,
                    message=f"missing required env var for provider '{provider}': {key}",
                    details={"provider": provider, "env": key},
                )
            )
    return errs


def normalize_exception(exc: Exception) -> DuroError:
    msg = str(exc)
    low = msg.lower()
    if "timeout" in low:
        return DuroError(ErrorCode.TIMEOUT, msg)
    if "schema" in low or "json" in low:
        return DuroError(ErrorCode.SCHEMA_ERROR, msg)
    if "api key" in low or "unauthorized" in low or "forbidden" in low:
        return DuroError(ErrorCode.PROVIDER_ERROR, msg)
    return DuroError(ErrorCode.UNKNOWN, msg)
