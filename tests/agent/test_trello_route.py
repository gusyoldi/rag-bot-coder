"""Tests for Trello vs RAG routing and missing credentials."""

from __future__ import annotations

from unittest.mock import patch

from src.agent.graph import detect_trello, route_after_detect
from src.agent.trello_agent import run_trello_agent


def test_detect_trello_sets_flag() -> None:
    assert detect_trello({"question": "listá boards en trello"})["wants_trello"] is True
    assert detect_trello({"question": "qué es RICE?"})["wants_trello"] is False


def test_route_after_detect() -> None:
    assert route_after_detect({"wants_trello": True}) == "trello"
    assert route_after_detect({"wants_trello": False}) == "rag"


def test_run_trello_agent_without_credentials(monkeypatch) -> None:
    monkeypatch.delenv("TRELLO_API_KEY", raising=False)
    monkeypatch.delenv("TRELLO_TOKEN", raising=False)
    with patch("src.agent.trello_agent._llm") as mock_llm:
        answer = run_trello_agent("listá mis boards de trello")
    mock_llm.assert_not_called()
    assert "TRELLO_API_KEY" in answer
    assert "TRELLO_TOKEN" in answer
