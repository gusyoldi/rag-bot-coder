"""Tool-calling loop for Trello board/card operations."""

from __future__ import annotations

import os
from functools import lru_cache

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama

from src.agent.state import AgentState
from src.mcp.client import credentials_configured
from src.mcp.tools import get_trello_tools, tools_by_name

MAX_TOOL_TURNS = 5

_SYSTEM = (
    "Sos un asistente que opera Trello vía tools. "
    "Respondé en español. "
    "Usá las tools para listar boards/listas, crear o mover cards. "
    "No inventes IDs: si no los tenés, llamá list_boards y list_lists primero. "
    "Cuando termines, respondé al usuario con un resumen claro "
    "(nombres, ids relevantes y URL si hay)."
)

_MISSING_CREDS = (
    "Para usar Trello necesitás configurar TRELLO_API_KEY y TRELLO_TOKEN en tu .env. "
    "Podés generarlos en https://trello.com/power-ups/admin (API key) "
    "y autorizar un token desde esa misma página."
)


@lru_cache(maxsize=1)
def _llm() -> ChatOllama:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return ChatOllama(model="llama3.1", base_url=base_url, temperature=0.2)


def run_trello_agent(question: str) -> str:
    """Run a bounded tool-calling loop and return the final answer text."""
    if not credentials_configured():
        return _MISSING_CREDS

    tools = get_trello_tools()
    registry = tools_by_name()
    llm = _llm().bind_tools(tools)
    messages: list = [
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=question),
    ]

    for _ in range(MAX_TOOL_TURNS):
        response = llm.invoke(messages)
        messages.append(response)
        tool_calls = getattr(response, "tool_calls", None) or []
        if not tool_calls:
            content = response.content
            if isinstance(content, str) and content.strip():
                return content.strip()
            return str(content)

        for call in tool_calls:
            name = call.get("name") if isinstance(call, dict) else getattr(call, "name", "")
            args = call.get("args") if isinstance(call, dict) else getattr(call, "args", {})
            call_id = (
                call.get("id") if isinstance(call, dict) else getattr(call, "id", name)
            )
            tool = registry.get(name or "")
            if tool is None:
                result = f"Error: tool desconocida '{name}'"
            else:
                result = tool.invoke(args or {})
            messages.append(
                ToolMessage(content=str(result), tool_call_id=call_id or name or "tool")
            )

    last = messages[-1]
    if isinstance(last, AIMessage):
        content = last.content
        return content.strip() if isinstance(content, str) else str(content)
    return "No pude completar la operación en Trello dentro del límite de intentos."


def trello_agent_node(state: AgentState) -> dict:
    """LangGraph node: answer a Trello request via tools."""
    answer = run_trello_agent(state["question"])
    return {"answer": answer, "finished": True, "wants_trello": True}
