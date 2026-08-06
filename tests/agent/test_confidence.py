"""Tests for rerank confidence aggregation."""

from __future__ import annotations

from src.agent.confidence import (
    CONFIDENCE_OK,
    CONFIDENCE_WEAK,
    max_rerank_confidence,
)


def test_max_rerank_confidence_empty():
    assert max_rerank_confidence([]) < CONFIDENCE_WEAK


def test_max_rerank_confidence_ok_band():
    score = max_rerank_confidence([-12.0, -8.0, -9.5])
    assert score == -8.0
    assert score >= CONFIDENCE_OK


def test_max_rerank_confidence_weak_band():
    score = max_rerank_confidence([-11.5, -12.0])
    assert score == -11.5
    assert score < CONFIDENCE_WEAK
