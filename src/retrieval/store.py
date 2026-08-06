"""Chroma vector store helpers."""

from __future__ import annotations

import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.retrieval.embeddings import get_embeddings


def persist_dir() -> Path:
    """Resolve Chroma persist directory from env (default ``./data/chroma``)."""
    return Path(os.getenv("CHROMA_PERSIST_DIR", "./data/chroma"))


def get_vector_store(collection_name: str) -> Chroma:
    """Open (or create) a Chroma collection for ``collection_name``."""
    return Chroma(
        collection_name=collection_name,
        persist_directory=str(persist_dir()),
        embedding_function=get_embeddings(),
    )


def collection_count(collection_name: str) -> int:
    """Return number of vectors already stored in the collection."""
    store = get_vector_store(collection_name)
    data = store.get()
    ids = data.get("ids") or []
    return len(ids)


def ingest_documents(
    documents: list[Document],
    collection_name: str,
    *,
    force: bool = False,
) -> int:
    """Persist ``documents`` into Chroma.

    If the collection already has vectors and ``force`` is False, skip and
    return 0. With ``force``, drop and recreate the collection first.
    """
    persist_dir().mkdir(parents=True, exist_ok=True)
    existing = collection_count(collection_name)

    if existing > 0 and not force:
        return 0

    if existing > 0 and force:
        store = get_vector_store(collection_name)
        store.delete_collection()

    store = get_vector_store(collection_name)
    store.add_documents(documents)
    return len(documents)
