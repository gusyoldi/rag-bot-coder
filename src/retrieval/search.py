"""Semantic search over the active domain collection."""

from __future__ import annotations

from src.domain import get_domain
from src.retrieval.store import get_vector_store


def search_documents(query: str, k: int = 3, *, domain_id: str | None = None) -> list[str]:
    """Return the ``k`` most similar document chunks for ``query``."""
    domain = get_domain(domain_id)
    store = get_vector_store(domain.id)
    docs = store.similarity_search(query=query, k=k)
    return [doc.page_content for doc in docs]
