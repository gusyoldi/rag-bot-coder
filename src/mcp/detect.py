"""Heuristic detector for Trello-related user queries."""

from __future__ import annotations

TRELLO_KEYWORDS = (
    "trello",
    "tablero",
    "tableros",
    "board",
    "boards",
    "tarjeta",
    "tarjetas",
    "card",
    "cards",
)


def wants_trello(text: str) -> bool:
    """Return True if ``text`` looks like a Trello board/card request."""
    lowered = (text or "").casefold()
    return any(keyword in lowered for keyword in TRELLO_KEYWORDS)
