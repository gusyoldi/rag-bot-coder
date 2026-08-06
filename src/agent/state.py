"""LangGraph state for the Plan B RAG loop."""

from __future__ import annotations

from typing import Literal, TypedDict


class CandidateDocState(TypedDict):
    content: str
    source: str
    vector_score: float


class RankedDocState(TypedDict):
    content: str
    source: str
    vector_score: float
    rerank_score: float


class AgentState(TypedDict):
    question: str
    intent: Literal["conceptual", "case", ""]
    candidates: list[CandidateDocState]
    retrieved_docs: list[str]
    ranked_docs: list[RankedDocState]
    confidence: float
    answer: str
    attempts: int
    finished: bool
    route: Literal["finish", "retry", "fallback", ""]
