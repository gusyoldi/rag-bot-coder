"""Integration smoke: full graph against local Ollama + Chroma."""

from __future__ import annotations

import pytest

from src.agent.graph import get_graph

pytestmark = pytest.mark.integration


def test_graph_answers_rice_question():
    graph = get_graph()
    result = graph.invoke(
        {
            "question": "explicame RICE",
            "intent": "",
            "candidates": [],
            "retrieved_docs": [],
            "ranked_docs": [],
            "confidence": 0.0,
            "answer": "",
            "attempts": 0,
            "finished": False,
            "route": "",
        }
    )
    assert result.get("answer")
    assert result.get("intent") in {"conceptual", "case"}
    assert "contexto suficiente" not in result["answer"].lower() or "rice" in result["answer"].lower()
