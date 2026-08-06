"""Shared fixtures for unit and integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.agent import graph as graph_module


@pytest.fixture(autouse=True)
def _clear_graph_caches():
    """Avoid cross-test pollution from lru_cache singletons."""
    graph_module._llm.cache_clear()
    graph_module.get_graph.cache_clear()
    yield
    graph_module._llm.cache_clear()
    graph_module.get_graph.cache_clear()


@pytest.fixture
def clean_domain_env(monkeypatch: pytest.MonkeyPatch):
    """Ensure DOMAIN_ID does not leak from the developer shell."""
    monkeypatch.delenv("DOMAIN_ID", raising=False)


@pytest.fixture
def tmp_corpus(tmp_path: Path) -> Path:
    """Create a tiny markdown corpus under a temporary directory."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "rice.md").write_text(
        "# RICE\n\nRICE is Reach, Impact, Confidence, Effort.\n",
        encoding="utf-8",
    )
    (corpus / "empty.md").write_text("   \n", encoding="utf-8")
    return corpus
