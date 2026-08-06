"""Confidence thresholds for rerank scores (ms-marco MiniLM logits)."""

# ms-marco MiniLM is English-centric: relevant Spanish queries against an
# English corpus land around -8..-10; off-topic Spanish around -11..-12;
# strong English hits can be positive (+1..+10). Thresholds calibrated with
# smoke queries on the product-owner corpus.
CONFIDENCE_OK = -10.0
CONFIDENCE_WEAK = -11.2


def max_rerank_confidence(rerank_scores: list[float]) -> float:
    """Aggregate confidence as the best rerank score (or very low if empty)."""
    if not rerank_scores:
        return CONFIDENCE_WEAK - 1.0
    return max(rerank_scores)
