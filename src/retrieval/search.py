"""Semantic search over the active domain collection."""

from __future__ import annotations

from src.domain import get_domain
from src.retrieval.store import get_vector_store


def search_documents(query: str, k: int = 3, *, domain_id: str | None = None) -> list[str]:
    """Return the ``k`` most similar document chunks for ``query``."""
    hits = search_documents_with_scores(query, k=k, domain_id=domain_id)
    return [content for content, _source, _score in hits]


def search_documents_with_scores(
    query: str,
    k: int = 20,
    *,
    domain_id: str | None = None,
) -> list[tuple[str, str, float]]:
    """Return ``(content, source, vector_score)`` for the top ``k`` hits.

    Note: Chroma/LangChain distance scores are lower-is-better; they are passed
    through for diagnostics. Reranking uses content, not this distance.
    """
    domain = get_domain(domain_id)
    store = get_vector_store(domain.id)
    results = store.similarity_search_with_score(query=query, k=k)
    return [
        (
            doc.page_content,
            str(doc.metadata.get("source", "unknown")),
            float(score),
        )
        for doc, score in results
    ]
