"""Domain-aware CLI entrypoint wired to the RAG agent graph."""

from __future__ import annotations

import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt

from src.agent.graph import get_graph
from src.domain import get_domain

console = Console()


def _run_query(query: str) -> str:
    graph = get_graph()
    result = graph.invoke(
        {
            "question": query,
            "retrieved_docs": [],
            "answer": "",
            "attempts": 0,
            "finished": False,
            "route": "",
        }
    )
    return result.get("answer") or "(sin respuesta)"


def main() -> None:
    load_dotenv()
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
                answer = _run_query(query)
        except Exception as exc:  # noqa: BLE001 — surface infra errors to CLI
            console.print(
                "[bold red]Error[/bold red]: no pude completar la consulta. "
                "Revisá que Ollama esté corriendo "
                "(`ollama serve`) y que el corpus esté ingerido "
                "(`python scripts/ingest_corpus.py`).\n"
                f"[dim]{exc}[/dim]"
            )
            continue

        console.print(f"[bold magenta]{domain.display_name}[/bold magenta]: {answer}\n")


if __name__ == "__main__":
    main()
    sys.exit(0)
