"""LangChain tools wrapping the Trello REST client."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import BaseTool, tool

from src.mcp.client import TrelloClient, TrelloError


def _client() -> TrelloClient:
    return TrelloClient()


@tool
def list_boards() -> str:
    """List open Trello boards for the authenticated user (id and name)."""
    try:
        boards = _client().list_boards()
    except TrelloError as exc:
        return f"Error: {exc}"
    slim = [{"id": b.get("id"), "name": b.get("name")} for b in boards]
    return json.dumps(slim, ensure_ascii=False)


@tool
def list_lists(board_id: str) -> str:
    """List open lists on a Trello board. Requires board_id from list_boards."""
    try:
        lists = _client().list_lists(board_id)
    except TrelloError as exc:
        return f"Error: {exc}"
    slim = [{"id": item.get("id"), "name": item.get("name")} for item in lists]
    return json.dumps(slim, ensure_ascii=False)


@tool
def create_card(id_list: str, name: str, desc: str = "") -> str:
    """Create a Trello card in the given list. Requires id_list from list_lists."""
    try:
        card = _client().create_card(id_list=id_list, name=name, desc=desc)
    except TrelloError as exc:
        return f"Error: {exc}"
    return json.dumps(
        {
            "id": card.get("id"),
            "name": card.get("name"),
            "idList": card.get("idList"),
            "url": card.get("url"),
        },
        ensure_ascii=False,
    )


@tool
def move_card(card_id: str, id_list: str) -> str:
    """Move an existing Trello card to another list. Requires card_id and id_list."""
    try:
        card = _client().move_card(card_id=card_id, id_list=id_list)
    except TrelloError as exc:
        return f"Error: {exc}"
    return json.dumps(
        {
            "id": card.get("id"),
            "name": card.get("name"),
            "idList": card.get("idList"),
            "url": card.get("url"),
        },
        ensure_ascii=False,
    )


TOOL_NAMES = ("list_boards", "list_lists", "create_card", "move_card")


def get_trello_tools() -> list[BaseTool]:
    """Return the Trello tools available to the agent."""
    return [list_boards, list_lists, create_card, move_card]


def tools_by_name() -> dict[str, Any]:
    """Map tool name → callable tool for the agent loop."""
    return {t.name: t for t in get_trello_tools()}
