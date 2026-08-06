"""Generic domain-aware CLI stub loop."""

from rich.console import Console
from rich.prompt import Prompt

from src.domain import get_domain

console = Console()


def main() -> None:
    domain = get_domain()
    exit_hint = " o ".join(f"[bold]{cmd}[/bold]" for cmd in sorted(domain.exit_commands))

    console.print(f"[bold cyan]{domain.display_name}[/bold cyan]")
    console.print(f"{domain.tagline} Escribí {exit_hint} para terminar.\n")

    while True:
        query = Prompt.ask("[bold green]vos[/bold green]").strip()
        if query.lower() in domain.exit_commands:
            console.print("¡Hasta luego!")
            break

        console.print(
            f"[dim]\\[stub][/dim] Dominio '{domain.id}' activo. "
            f"Todavía no hay retrieval: {query}"
        )


if __name__ == "__main__":
    main()
