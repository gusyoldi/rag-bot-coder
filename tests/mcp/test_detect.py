"""Tests for Trello query detector."""

from __future__ import annotations

from src.mcp.detect import wants_trello


def test_detects_trello_keywords() -> None:
    assert wants_trello("listá mis boards de trello")
    assert wants_trello("Creá una tarjeta en el tablero Product")
    assert wants_trello("Move card to Done")


def test_ignores_unrelated_queries() -> None:
    assert not wants_trello("qué es RICE?")
    assert not wants_trello("explicame JTBD")
    assert not wants_trello("")
