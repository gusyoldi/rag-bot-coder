"""RAG graph: detect Trello → RAG loop | Trello tool agent."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

from src.agent.confidence import (
    CONFIDENCE_OK,
    CONFIDENCE_WEAK,
    max_rerank_confidence,
)
from src.agent.state import AgentState, CandidateDocState, RankedDocState
from src.agent.trello_agent import trello_agent_node
from src.domain import get_domain
from src.mcp.detect import wants_trello
from src.orchestration.prompts import (
    build_answer_prompt,
    build_intent_prompt,
    build_refine_prompt,
    fallback_message,
)
from src.ranking.reranker import rerank
from src.retrieval.search import search_documents_with_scores

MAX_ATTEMPTS = 3
RETRIEVE_K = 20
RERANK_TOP_K = 5


@lru_cache(maxsize=1)
def _llm() -> ChatOllama:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return ChatOllama(model="llama3.1", base_url=base_url, temperature=0.2)


def _parse_intent(raw: str) -> Literal["conceptual", "case"]:
    text = raw.strip().lower()
    if "case" in text or "caso" in text:
        return "case"
    return "conceptual"


def detect_trello(state: AgentState) -> dict:
    """Flag Trello board/card requests for the tool-calling path."""
    return {"wants_trello": wants_trello(state["question"])}


def route_after_detect(state: AgentState) -> Literal["trello", "rag"]:
    if state.get("wants_trello"):
        return "trello"
    return "rag"


def interpret_intent(state: AgentState) -> dict:
    response = _llm().invoke(build_intent_prompt(state["question"]))
    content = response.content if isinstance(response.content, str) else str(response.content)
    return {"intent": _parse_intent(content)}


def retrieve(state: AgentState) -> dict:
    hits = search_documents_with_scores(state["question"], k=RETRIEVE_K)
    candidates: list[CandidateDocState] = [
        CandidateDocState(content=content, source=source, vector_score=score)
        for content, source, score in hits
    ]
    return {
        "candidates": candidates,
        "retrieved_docs": [content for content, _source, _score in hits],
    }


def rerank_docs(state: AgentState) -> dict:
    candidates = [
        (doc["content"], doc["source"], float(doc["vector_score"]))
        for doc in state.get("candidates") or []
    ]
    ranked = rerank(state["question"], candidates, top_k=RERANK_TOP_K)
    ranked_state: list[RankedDocState] = [
        RankedDocState(
            content=doc.content,
            source=doc.source,
            vector_score=doc.vector_score,
            rerank_score=doc.rerank_score,
        )
        for doc in ranked
    ]
    confidence = max_rerank_confidence([doc.rerank_score for doc in ranked])
    return {
        "ranked_docs": ranked_state,
        "retrieved_docs": [doc.content for doc in ranked],
        "confidence": confidence,
    }


def generate(state: AgentState) -> dict:
    domain = get_domain()
    docs = state.get("ranked_docs") or []
    context = "\n\n---\n\n".join(doc["content"] for doc in docs)
    intent = state.get("intent") or "conceptual"
    if intent not in ("conceptual", "case"):
        intent = "conceptual"
    prompt = build_answer_prompt(
        system_prompt=domain.system_prompt,
        context=context,
        question=state["question"],
        intent=intent,
    )
    response = _llm().invoke(prompt)
    content = response.content if isinstance(response.content, str) else str(response.content)
    return {"answer": content}


def assess(state: AgentState) -> dict:
    """Route by rerank confidence; persist attempt count."""
    confidence = float(state.get("confidence") or CONFIDENCE_WEAK - 1.0)

    if confidence >= CONFIDENCE_OK:
        return {"finished": True, "route": "finish"}

    attempts = state["attempts"] + 1
    if confidence < CONFIDENCE_WEAK and attempts >= MAX_ATTEMPTS:
        return {"attempts": attempts, "route": "fallback"}
    if attempts >= MAX_ATTEMPTS:
        return {"attempts": attempts, "finished": True, "route": "finish"}
    return {"attempts": attempts, "route": "retry"}


def route_after_assess(state: AgentState) -> Literal["finish", "retry", "fallback"]:
    route = state.get("route") or "fallback"
    if route == "finish":
        return "finish"
    if route == "retry":
        return "retry"
    return "fallback"


def refine(state: AgentState) -> dict:
    intent = state.get("intent") or "conceptual"
    if intent not in ("conceptual", "case"):
        intent = "conceptual"
    prompt = build_refine_prompt(state["question"], intent)
    response = _llm().invoke(prompt)
    rewritten = response.content if isinstance(response.content, str) else str(response.content)
    rewritten = rewritten.strip().strip('"').strip("'")
    if not rewritten:
        rewritten = f"{state['question']} product owner framework"
    return {"question": rewritten}


def fallback(state: AgentState) -> dict:
    domain = get_domain()
    return {
        "answer": fallback_message(domain),
        "finished": True,
    }


def build_graph():
    """Compile the Plan B LangGraph agent with optional Trello tools path."""
    builder = StateGraph(AgentState)
    builder.add_node("detect_trello", detect_trello)
    builder.add_node("trello_agent", trello_agent_node)
    builder.add_node("interpret_intent", interpret_intent)
    builder.add_node("retrieve", retrieve)
    builder.add_node("rerank", rerank_docs)
    builder.add_node("generate", generate)
    builder.add_node("assess", assess)
    builder.add_node("refine", refine)
    builder.add_node("fallback", fallback)

    builder.set_entry_point("detect_trello")
    builder.add_conditional_edges(
        "detect_trello",
        route_after_detect,
        {
            "trello": "trello_agent",
            "rag": "interpret_intent",
        },
    )
    builder.add_edge("trello_agent", END)
    builder.add_edge("interpret_intent", "retrieve")
    builder.add_edge("retrieve", "rerank")
    builder.add_edge("rerank", "generate")
    builder.add_edge("generate", "assess")
    builder.add_conditional_edges(
        "assess",
        route_after_assess,
        {
            "finish": END,
            "retry": "refine",
            "fallback": "fallback",
        },
    )
    builder.add_edge("refine", "retrieve")
    builder.add_edge("fallback", END)
    return builder.compile()


@lru_cache(maxsize=1)
def get_graph():
    return build_graph()
