"""Domain-aware CLI entrypoint wired to the RAG agent graph."""

from __future__ import annotations

import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt

from src.domain import get_domain
from src.observability import configure_observability

console = Console()


def get_graph():
    """Lazy import so Phoenix can instrument LangGraph before it loads."""
    from src.agent.graph import get_graph as _get_graph

    return _get_graph()


def _run_query(query: str) -> dict:
    graph = get_graph()
    return graph.invoke(
        {
            "question": query,
            "intent": "",
            "candidates": [],
            "retrieved_docs": [],
            "ranked_docs": [],
            "confidence": 0.0,
            "answer": "",
            "attempts": 0,
            "finished": False,
            "route": "",
            "wants_trello": False,
        }
    )


def main() -> None:
    load_dotenv()
    configure_observability()
    domain = get_domain()
    exit_hint = " o ".join(f"[bold]{cmd}[/bold]" for cmd in sorted(domain.exit_commands))

    console.print(f"[bold cyan]{domain.display_name}[/bold cyan]")
    console.print(f"{domain.tagline} Escribí {exit_hint} para terminar.\n")

    while True:
        query = Prompt.ask("[bold green]vos[/bold green]").strip()
        if query.lower() in domain.exit_commands:
            console.print("¡Hasta luego!")
            break
        if not query:
            continue

        try:
            with console.status("[dim]Pensando…[/dim]", spinner="dots"):
                result = _run_query(query)
        except Exception as exc:  # noqa: BLE001 — surface infra errors to CLI
            console.print(
                "[bold red]Error[/bold red]: no pude completar la consulta. "
                "Revisá que Ollama esté corriendo "
                "(`ollama serve`) y que el corpus esté ingerido "
                "(`python scripts/ingest_corpus.py`). "
                "La primera consulta puede tardar al cargar el cross-encoder.\n"
                f"[dim]{exc}[/dim]"
            )
            continue

        intent = result.get("intent") or "?"
        confidence = result.get("confidence")
        conf_txt = f"{confidence:.2f}" if isinstance(confidence, (int, float)) else "?"
        console.print(
            f"[dim]intent={intent} · confidence={conf_txt}[/dim]"
        )
        answer = result.get("answer") or "(sin respuesta)"
        console.print(f"[bold magenta]{domain.display_name}[/bold magenta]: {answer}\n")


if __name__ == "__main__":
    main()
    sys.exit(0)
