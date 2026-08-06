"""Cross-encoder reranking (CLASE 6 pattern)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Sequence

from sentence_transformers import CrossEncoder

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
DEFAULT_TOP_K = 5


@dataclass(frozen=True)
class RankedDoc:
    content: str
    source: str
    vector_score: float
    rerank_score: float

    def to_dict(self) -> dict:
        return asdict(self)


@lru_cache(maxsize=1)
def _encoder() -> CrossEncoder:
    """Lazy singleton — first call downloads/loads the model (cold start)."""
    return CrossEncoder(RERANKER_MODEL)


def rerank(
    query: str,
    candidates: Sequence[tuple[str, str, float]],
    *,
    top_k: int = DEFAULT_TOP_K,
) -> list[RankedDoc]:
    """Rerank ``(content, source, vector_score)`` candidates for ``query``.

    Returns the top ``top_k`` documents sorted by ``rerank_score`` descending.
    """
    if not candidates:
        return []

    pairs = [[query, content] for content, _source, _score in candidates]
    scores = _encoder().predict(pairs)

    ranked = [
        RankedDoc(
            content=content,
            source=source,
            vector_score=float(vector_score),
            rerank_score=float(rerank_score),
        )
        for (content, source, vector_score), rerank_score in zip(
            candidates, scores, strict=True
        )
    ]
    ranked.sort(key=lambda doc: doc.rerank_score, reverse=True)
    return ranked[:top_k]
