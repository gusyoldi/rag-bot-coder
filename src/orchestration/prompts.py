"""Prompt builders for grounded PO coaching answers."""

from __future__ import annotations

from src.domain import DomainConfig


def build_answer_prompt(
    *,
    system_prompt: str,
    context: str,
    question: str,
) -> str:
    """Build the generation prompt with retrieved context."""
    return (
        f"{system_prompt}\n\n"
        "Contexto recuperado:\n"
        f"{context if context.strip() else '(vacío)'}\n\n"
        "Pregunta del usuario:\n"
        f"{question}\n\n"
        "Respuesta:"
    )


def build_refine_prompt(question: str) -> str:
    """Ask the LLM to rewrite a query for better retrieval."""
    return (
        "Reescribí la siguiente consulta de Product Owner para mejorar la "
        "búsqueda en una base de conocimiento sobre RICE, JTBD, user stories "
        "y product discovery. Devolvé solo la consulta reescrita, sin comillas "
        "ni explicación.\n\n"
        f"Consulta original: {question}"
    )


def fallback_message(domain: DomainConfig) -> str:
    """Message when retrieval never yields usable context."""
    return (
        f"No encontré contexto suficiente en la base de conocimiento de "
        f"{domain.display_name} para responder con confianza. "
        "Probá reformular la pregunta o ampliá el corpus."
    )
