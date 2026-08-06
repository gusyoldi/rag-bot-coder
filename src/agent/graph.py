"""Cyclic RAG graph: retrieve → generate → assess → refine|fallback|END."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

from src.agent.state import AgentState
from src.domain import get_domain
from src.orchestration.prompts import (
    build_answer_prompt,
    build_refine_prompt,
    fallback_message,
)
from src.retrieval.search import search_documents

MAX_ATTEMPTS = 3


@lru_cache(maxsize=1)
def _llm() -> ChatOllama:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return ChatOllama(model="llama3.1", base_url=base_url, temperature=0.2)


def retrieve(state: AgentState) -> dict:
    docs = search_documents(state["question"], k=3)
    return {"retrieved_docs": docs}


def generate(state: AgentState) -> dict:
    domain = get_domain()
    context = "\n\n---\n\n".join(state["retrieved_docs"])
    prompt = build_answer_prompt(
        system_prompt=domain.system_prompt,
        context=context,
        question=state["question"],
    )
    response = _llm().invoke(prompt)
    content = response.content if isinstance(response.content, str) else str(response.content)
    return {"answer": content}


def assess(state: AgentState) -> dict:
    """Decide next route and persist attempt count in state."""
    if state["retrieved_docs"]:
        return {"finished": True, "route": "finish"}

    attempts = state["attempts"] + 1
    if attempts >= MAX_ATTEMPTS:
        return {"attempts": attempts, "route": "fallback"}
    return {"attempts": attempts, "route": "retry"}


def route_after_assess(state: AgentState) -> Literal["finish", "retry", "fallback"]:
    route = state.get("route") or "fallback"
    if route == "finish":
        return "finish"
    if route == "retry":
        return "retry"
    return "fallback"


def refine(state: AgentState) -> dict:
    prompt = build_refine_prompt(state["question"])
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
    """Compile the Plan A LangGraph agent."""
    builder = StateGraph(AgentState)
    builder.add_node("retrieve", retrieve)
    builder.add_node("generate", generate)
    builder.add_node("assess", assess)
    builder.add_node("refine", refine)
    builder.add_node("fallback", fallback)

    builder.set_entry_point("retrieve")
    builder.add_edge("retrieve", "generate")
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
