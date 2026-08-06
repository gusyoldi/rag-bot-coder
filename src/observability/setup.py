"""Env-gated LangSmith + Phoenix bootstrap for the RAG agent."""

from __future__ import annotations

import os
import sys

_configured = False

_TRUTHY = frozenset({"1", "true", "yes", "on"})
_DEFAULT_PROJECT = "po-copilot"
_DEFAULT_PHOENIX_ENDPOINT = "http://localhost:6006"


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in _TRUTHY


def _warn(message: str) -> None:
    print(f"[observability] {message}", file=sys.stderr)


def _configure_langsmith() -> None:
    api_key = os.getenv("LANGSMITH_API_KEY", "").strip()
    if not api_key:
        legacy = os.getenv("LANGCHAIN_API_KEY", "").strip()
        if legacy:
            os.environ["LANGSMITH_API_KEY"] = legacy
            api_key = legacy

    if not api_key:
        return

    # Key present ⇒ enable tracing (remove the key to disable).
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ.setdefault("LANGSMITH_PROJECT", _DEFAULT_PROJECT)
    # Legacy alias still honored by older LangChain stacks.
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ.setdefault("LANGCHAIN_PROJECT", os.environ["LANGSMITH_PROJECT"])


def _configure_phoenix() -> None:
    if not _env_truthy("PHOENIX_ENABLED"):
        return

    project = os.getenv("PHOENIX_PROJECT", os.getenv("LANGSMITH_PROJECT", _DEFAULT_PROJECT))
    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", _DEFAULT_PHOENIX_ENDPOINT)

    try:
        from phoenix.otel import register
        from openinference.instrumentation.langchain import LangChainInstrumentor
    except ImportError as exc:
        _warn(f"Phoenix deps missing ({exc}); skipping local tracing.")
        return

    try:
        tracer_provider = register(
            project_name=project,
            endpoint=endpoint,
            batch=True,
        )
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
    except Exception as exc:  # noqa: BLE001 — observability must not kill the CLI
        _warn(f"Phoenix setup failed ({exc}); continuing without local tracing.")


def configure_observability() -> None:
    """Enable LangSmith and/or Phoenix based on environment variables.

    Safe to call multiple times. Failures are reported to stderr and ignored.
    """
    global _configured
    if _configured:
        return

    try:
        _configure_langsmith()
        _configure_phoenix()
    except Exception as exc:  # noqa: BLE001
        _warn(f"setup failed ({exc}); continuing without tracing.")
    finally:
        _configured = True


def reset_observability_for_tests() -> None:
    """Clear the idempotency flag (unit tests only)."""
    global _configured
    _configured = False
