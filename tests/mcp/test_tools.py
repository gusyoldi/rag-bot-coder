"""Tests for Trello LangChain tools."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from src.mcp.tools import TOOL_NAMES, create_card, get_trello_tools, list_boards


def test_get_trello_tools_exposes_expected_names() -> None:
    names = {t.name for t in get_trello_tools()}
    assert names == set(TOOL_NAMES)


def test_list_boards_tool_returns_json() -> None:
    mock_client = MagicMock()
    mock_client.list_boards.return_value = [{"id": "b1", "name": "PO", "closed": False}]
    with patch("src.mcp.tools._client", return_value=mock_client):
        result = list_boards.invoke({})
    assert json.loads(result) == [{"id": "b1", "name": "PO"}]


def test_create_card_tool_calls_client() -> None:
    mock_client = MagicMock()
    mock_client.create_card.return_value = {
        "id": "c1",
        "name": "Story",
        "idList": "l1",
        "url": "https://trello.com/c/c1",
    }
    with patch("src.mcp.tools._client", return_value=mock_client):
        result = create_card.invoke(
            {"id_list": "l1", "name": "Story", "desc": "detalle"}
        )
    mock_client.create_card.assert_called_once_with(
        id_list="l1", name="Story", desc="detalle"
    )
    data = json.loads(result)
    assert data["id"] == "c1"
    assert data["url"] == "https://trello.com/c/c1"
