"""Minimal Trello REST client (API key + token)."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TRELLO_API_BASE = "https://api.trello.com/1"


class TrelloError(RuntimeError):
    """Raised when the Trello API returns an error or credentials are missing."""


def credentials_configured() -> bool:
    """Return True when both Trello env credentials are non-empty."""
    key = (os.getenv("TRELLO_API_KEY") or "").strip()
    token = (os.getenv("TRELLO_TOKEN") or "").strip()
    return bool(key and token)


class TrelloClient:
    """Thin wrapper around Trello REST v1 for boards, lists, and cards."""

    def __init__(
        self,
        api_key: str | None = None,
        token: str | None = None,
        *,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = (api_key if api_key is not None else os.getenv("TRELLO_API_KEY") or "").strip()
        self.token = (token if token is not None else os.getenv("TRELLO_TOKEN") or "").strip()
        self.timeout = timeout
        if not self.api_key or not self.token:
            raise TrelloError(
                "Faltan TRELLO_API_KEY y/o TRELLO_TOKEN. Configuralos en .env."
            )

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> Any:
        query = {"key": self.api_key, "token": self.token}
        if params:
            query.update({k: v for k, v in params.items() if v is not None})
        url = f"{TRELLO_API_BASE}{path}?{urlencode(query)}"
        data = None
        headers = {"Accept": "application/json"}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            raise TrelloError(f"Trello API {exc.code}: {detail or exc.reason}") from exc
        except URLError as exc:
            raise TrelloError(f"No pude conectar con Trello: {exc.reason}") from exc
        if not raw:
            return None
        return json.loads(raw.decode("utf-8"))

    def list_boards(self) -> list[dict[str, Any]]:
        result = self._request(
            "GET",
            "/members/me/boards",
            params={"fields": "id,name,closed", "filter": "open"},
        )
        return list(result or [])

    def list_lists(self, board_id: str) -> list[dict[str, Any]]:
        result = self._request(
            "GET",
            f"/boards/{board_id}/lists",
            params={"fields": "id,name,closed", "filter": "open"},
        )
        return list(result or [])

    def create_card(
        self,
        id_list: str,
        name: str,
        desc: str = "",
    ) -> dict[str, Any]:
        result = self._request(
            "POST",
            "/cards",
            body={"idList": id_list, "name": name, "desc": desc},
        )
        return dict(result or {})

    def move_card(self, card_id: str, id_list: str) -> dict[str, Any]:
        result = self._request(
            "PUT",
            f"/cards/{card_id}",
            body={"idList": id_list},
        )
        return dict(result or {})
