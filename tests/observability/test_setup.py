"""Unit tests for env-gated observability bootstrap."""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

import pytest

from src.observability import setup as obs_setup


@pytest.fixture(autouse=True)
def _reset_obs(monkeypatch: pytest.MonkeyPatch):
    obs_setup.reset_observability_for_tests()
    for key in (
        "LANGSMITH_API_KEY",
        "LANGCHAIN_API_KEY",
        "LANGSMITH_TRACING",
        "LANGSMITH_PROJECT",
        "LANGCHAIN_TRACING_V2",
        "LANGCHAIN_PROJECT",
        "PHOENIX_ENABLED",
        "PHOENIX_COLLECTOR_ENDPOINT",
        "PHOENIX_PROJECT",
    ):
        monkeypatch.delenv(key, raising=False)
    yield
    obs_setup.reset_observability_for_tests()


def test_noop_without_keys_or_phoenix():
    obs_setup.configure_observability()
    assert "LANGSMITH_TRACING" not in obs_setup.os.environ


def test_langsmith_from_api_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test-key")
    obs_setup.configure_observability()
    assert obs_setup.os.environ["LANGSMITH_TRACING"] == "true"
    assert obs_setup.os.environ["LANGSMITH_PROJECT"] == "po-copilot"


def test_langsmith_from_legacy_langchain_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LANGCHAIN_API_KEY", "legacy-key")
    obs_setup.configure_observability()
    assert obs_setup.os.environ["LANGSMITH_API_KEY"] == "legacy-key"
    assert obs_setup.os.environ["LANGSMITH_TRACING"] == "true"


def test_phoenix_instruments_when_enabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PHOENIX_ENABLED", "true")
    monkeypatch.setenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006")

    tracer = object()
    register = MagicMock(return_value=tracer)
    instrumentor = MagicMock()
    instrumentor_cls = MagicMock(return_value=instrumentor)

    phoenix_otel = types.ModuleType("phoenix.otel")
    phoenix_otel.register = register
    sys.modules["phoenix"] = types.ModuleType("phoenix")
    sys.modules["phoenix.otel"] = phoenix_otel

    oi_lc = types.ModuleType("openinference.instrumentation.langchain")
    oi_lc.LangChainInstrumentor = instrumentor_cls
    sys.modules["openinference"] = types.ModuleType("openinference")
    sys.modules["openinference.instrumentation"] = types.ModuleType(
        "openinference.instrumentation"
    )
    sys.modules["openinference.instrumentation.langchain"] = oi_lc

    obs_setup.configure_observability()

    register.assert_called_once()
    kwargs = register.call_args.kwargs
    assert kwargs["endpoint"] == "http://localhost:6006"
    assert kwargs["project_name"] == "po-copilot"
    instrumentor.instrument.assert_called_once_with(tracer_provider=tracer)


def test_configure_is_idempotent(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test-key")
    calls: list[str] = []

    original = obs_setup._configure_langsmith

    def tracked() -> None:
        calls.append("langsmith")
        original()

    monkeypatch.setattr(obs_setup, "_configure_langsmith", tracked)
    obs_setup.configure_observability()
    obs_setup.configure_observability()
    assert calls == ["langsmith"]
