"""Unit tests for LangGraph nodes with mocked LLM / retrieval / rerank."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.agent import graph as graph_module
from src.agent.confidence import CONFIDENCE_OK, CONFIDENCE_WEAK
from src.agent.graph import (
    MAX_ATTEMPTS,
    _parse_intent,
    assess,
    fallback,
    generate,
    interpret_intent,
    refine,
    rerank_docs,
    retrieve,
    route_after_assess,
)
from src.ranking.reranker import RankedDoc


def _base_state(**overrides):
    state = {
        "question": "qué es RICE?",
        "intent": "conceptual",
        "candidates": [],
        "retrieved_docs": [],
        "ranked_docs": [],
        "confidence": 0.0,
        "answer": "",
        "attempts": 0,
        "finished": False,
        "route": "",
    }
    state.update(overrides)
    return state


def test_parse_intent_case_and_conceptual():
    assert _parse_intent("case") == "case"
    assert _parse_intent("CASO práctico") == "case"
    assert _parse_intent("conceptual") == "conceptual"
    assert _parse_intent("teoría") == "conceptual"


def test_assess_finish_when_ok():
    result = assess(_base_state(confidence=CONFIDENCE_OK + 1, attempts=0))
    assert result["route"] == "finish"
    assert result["finished"] is True


def test_assess_retry_when_between_ok_and_weak():
    mid = (CONFIDENCE_OK + CONFIDENCE_WEAK) / 2
    result = assess(_base_state(confidence=mid, attempts=0))
    assert result["route"] == "retry"
    assert result["attempts"] == 1


def test_assess_fallback_when_very_weak_and_max_attempts():
    result = assess(
        _base_state(
            confidence=CONFIDENCE_WEAK - 1,
            attempts=MAX_ATTEMPTS - 1,
        )
    )
    assert result["route"] == "fallback"
    assert result["attempts"] == MAX_ATTEMPTS


def test_assess_finish_when_weak_but_attempts_exhausted():
    mid = (CONFIDENCE_OK + CONFIDENCE_WEAK) / 2
    result = assess(_base_state(confidence=mid, attempts=MAX_ATTEMPTS - 1))
    assert result["route"] == "finish"
    assert result["finished"] is True


def test_route_after_assess():
    assert route_after_assess(_base_state(route="finish")) == "finish"
    assert route_after_assess(_base_state(route="retry")) == "retry"
    assert route_after_assess(_base_state(route="fallback")) == "fallback"
    assert route_after_assess(_base_state(route="")) == "fallback"


def test_interpret_intent_uses_llm(monkeypatch: pytest.MonkeyPatch):
    fake = MagicMock()
    fake.invoke.return_value = SimpleNamespace(content="case")
    monkeypatch.setattr(graph_module, "_llm", lambda: fake)

    result = interpret_intent(_base_state(question="priorizá estas 3 features"))
    assert result["intent"] == "case"
    fake.invoke.assert_called_once()


def test_retrieve_maps_candidates(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        graph_module,
        "search_documents_with_scores",
        lambda query, k=20: [("doc a", "a.md", 0.1), ("doc b", "b.md", 0.2)],
    )
    result = retrieve(_base_state())
    assert result["retrieved_docs"] == ["doc a", "doc b"]
    assert result["candidates"][0]["source"] == "a.md"


def test_rerank_docs_sets_confidence(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        graph_module,
        "rerank",
        lambda query, candidates, top_k=5: [
            RankedDoc("top", "rice.md", 0.1, -8.0),
            RankedDoc("other", "jtbd.md", 0.2, -12.0),
        ],
    )
    state = _base_state(
        candidates=[
            {"content": "top", "source": "rice.md", "vector_score": 0.1},
            {"content": "other", "source": "jtbd.md", "vector_score": 0.2},
        ]
    )
    result = rerank_docs(state)
    assert result["confidence"] == -8.0
    assert result["ranked_docs"][0]["source"] == "rice.md"
    assert result["retrieved_docs"] == ["top", "other"]


def test_generate_uses_ranked_context(monkeypatch: pytest.MonkeyPatch):
    fake = MagicMock()
    fake.invoke.return_value = SimpleNamespace(content="respuesta mock")
    monkeypatch.setattr(graph_module, "_llm", lambda: fake)

    result = generate(
        _base_state(
            intent="case",
            ranked_docs=[
                {
                    "content": "RICE context",
                    "source": "rice.md",
                    "vector_score": 0.1,
                    "rerank_score": -8.0,
                }
            ],
        )
    )
    assert result["answer"] == "respuesta mock"
    prompt = fake.invoke.call_args.args[0]
    assert "RICE context" in prompt
    assert "Modo caso práctico" in prompt


def test_refine_rewrites_question(monkeypatch: pytest.MonkeyPatch):
    fake = MagicMock()
    fake.invoke.return_value = SimpleNamespace(content='"RICE prioritization framework"')
    monkeypatch.setattr(graph_module, "_llm", lambda: fake)

    result = refine(_base_state(question="priorizar", intent="conceptual"))
    assert result["question"] == "RICE prioritization framework"


def test_refine_fallback_when_empty_rewrite(monkeypatch: pytest.MonkeyPatch):
    fake = MagicMock()
    fake.invoke.return_value = SimpleNamespace(content="   ")
    monkeypatch.setattr(graph_module, "_llm", lambda: fake)

    result = refine(_base_state(question="hola", intent="case"))
    assert "hola" in result["question"]
    assert "product owner" in result["question"]


def test_fallback_message(clean_domain_env):
    result = fallback(_base_state())
    assert result["finished"] is True
    assert "contexto suficiente" in result["answer"]
