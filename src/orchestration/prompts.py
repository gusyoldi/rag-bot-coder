"""Prompt builders for grounded PO coaching answers."""

from __future__ import annotations

from typing import Literal

from src.domain import DomainConfig

Intent = Literal["conceptual", "case"]


def build_intent_prompt(question: str) -> str:
    """Classify whether the user wants theory or a practical case."""
    return (
        "Clasificá la consulta del usuario en exactamente una etiqueta:\n"
        "- conceptual: pide definición, explicación o teoría de un marco\n"
        "- case: trae un escenario concreto y quiere aplicar un marco\n\n"
        "Respondé solo con una palabra: conceptual o case.\n\n"
        f"Consulta: {question}"
    )


def build_answer_prompt(
    *,
    system_prompt: str,
    context: str,
    question: str,
    intent: Intent,
) -> str:
    """Build the generation prompt with retrieved context and intent mode."""
    if intent == "case":
        mode = (
            "Modo caso práctico: aplicá el marco del contexto al escenario del "
            "usuario. Sé concreto (pasos, criterios, trade-offs). No te limites "
            "a definir el marco."
        )
    else:
        mode = (
            "Modo conceptual: explicá el marco con claridad usando el contexto. "
            "Podés dar un ejemplo breve, pero priorizá la comprensión del marco."
        )

    return (
        f"{system_prompt}\n\n"
        f"{mode}\n\n"
        "Contexto recuperado:\n"
        f"{context if context.strip() else '(vacío)'}\n\n"
        "Pregunta del usuario:\n"
        f"{question}\n\n"
        "Respuesta:"
    )


def build_refine_prompt(question: str, intent: Intent) -> str:
    """Ask the LLM to rewrite a query for better retrieval."""
    if intent == "case":
        focus = (
            "Enfocá la reescritura en el marco de priorización/producto "
            "relevante (RICE, JTBD, user stories, discovery) y en los "
            "elementos del caso que ayudan a recuperarlo."
        )
    else:
        focus = (
            "Enfocá la reescritura en términos de definición y componentes "
            "del marco (RICE, JTBD, user stories, discovery)."
        )

    return (
        "Reescribí la siguiente consulta de Product Owner para mejorar la "
        "búsqueda en una base de conocimiento. "
        f"{focus} "
        "Devolvé solo la consulta reescrita, sin comillas ni explicación.\n\n"
        f"Consulta original: {question}"
    )


def fallback_message(domain: DomainConfig) -> str:
    """Message when retrieval never yields usable context."""
    return (
        f"No encontré contexto suficiente en la base de conocimiento de "
        f"{domain.display_name} para responder con confianza. "
        "Probá reformular la pregunta o ampliá el corpus."
    )
