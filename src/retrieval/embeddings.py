"""Ollama embedding model factory."""

from __future__ import annotations

import os

from langchain_ollama import OllamaEmbeddings


def get_embeddings() -> OllamaEmbeddings:
    """Return embeddings backed by ``nomic-embed-text`` via Ollama."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return OllamaEmbeddings(model="nomic-embed-text", base_url=base_url)
