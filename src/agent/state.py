"""LangGraph state for the Plan A RAG loop."""

from __future__ import annotations

from typing import Literal, TypedDict


class AgentState(TypedDict):
    question: str
    retrieved_docs: list[str]
    answer: str
    attempts: int
    finished: bool
    route: Literal["finish", "retry", "fallback", ""]
