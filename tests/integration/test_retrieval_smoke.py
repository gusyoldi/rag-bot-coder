"""Integration smoke: real Chroma + Ollama embeddings."""

from __future__ import annotations

import pytest

from src.retrieval.search import search_documents

pytestmark = pytest.mark.integration


def test_search_documents_finds_rice():
    docs = search_documents("RICE prioritization", k=3)
    assert docs, "Expected retrieved chunks; run: python scripts/ingest_corpus.py"
    joined = "\n".join(docs).lower()
    assert "rice" in joined
