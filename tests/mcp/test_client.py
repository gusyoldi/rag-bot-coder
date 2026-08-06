"""Tests for Trello REST client (mocked HTTP)."""

from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import patch

import pytest

from src.mcp.client import TrelloClient, TrelloError, credentials_configured


def test_credentials_configured_true(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRELLO_API_KEY", "key")
    monkeypatch.setenv("TRELLO_TOKEN", "token")
    assert credentials_configured() is True


def test_credentials_configured_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TRELLO_API_KEY", raising=False)
    monkeypatch.delenv("TRELLO_TOKEN", raising=False)
    assert credentials_configured() is False


def test_list_boards_parses_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRELLO_API_KEY", "k")
    monkeypatch.setenv("TRELLO_TOKEN", "t")
    payload = [{"id": "b1", "name": "Product"}]
    fake = BytesIO(json.dumps(payload).encode())
    fake.status = 200  # type: ignore[attr-defined]

    with patch("src.mcp.client.urlopen", return_value=fake) as mock_open:
        client = TrelloClient()
        boards = client.list_boards()

    assert boards == payload
    req = mock_open.call_args.args[0]
    assert "key=k" in req.full_url
    assert "token=t" in req.full_url
    assert "/1/members/me/boards" in req.full_url


def test_create_card_posts_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRELLO_API_KEY", "k")
    monkeypatch.setenv("TRELLO_TOKEN", "t")
    payload = {"id": "c1", "name": "Story", "idList": "l1"}
    fake = BytesIO(json.dumps(payload).encode())
    fake.status = 200  # type: ignore[attr-defined]

    with patch("src.mcp.client.urlopen", return_value=fake) as mock_open:
        client = TrelloClient()
        card = client.create_card(id_list="l1", name="Story", desc="desc")

    assert card["id"] == "c1"
    req = mock_open.call_args.args[0]
    assert req.get_method() == "POST"
    body = json.loads(req.data.decode())
    assert body["idList"] == "l1"
    assert body["name"] == "Story"
    assert body["desc"] == "desc"


def test_http_error_raises_trello_error(monkeypatch: pytest.MonkeyPatch) -> None:
    from urllib.error import HTTPError

    monkeypatch.setenv("TRELLO_API_KEY", "k")
    monkeypatch.setenv("TRELLO_TOKEN", "t")
    err = HTTPError(
        url="https://api.trello.com/1/members/me/boards",
        code=401,
        msg="Unauthorized",
        hdrs=None,
        fp=BytesIO(b"bad auth"),
    )
    with patch("src.mcp.client.urlopen", side_effect=err):
        client = TrelloClient()
        with pytest.raises(TrelloError, match="401"):
            client.list_boards()
