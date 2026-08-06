"""Tests for prompt builders."""

from __future__ import annotations

from src.domain import get_domain
from src.orchestration.prompts import (
    build_answer_prompt,
    build_intent_prompt,
    build_refine_prompt,
    fallback_message,
)


def test_build_intent_prompt_includes_question():
    prompt = build_intent_prompt("qué es RICE?")
    assert "qué es RICE?" in prompt
    assert "conceptual" in prompt
    assert "case" in prompt


def test_build_answer_prompt_conceptual_vs_case():
    conceptual = build_answer_prompt(
        system_prompt="sys",
        context="ctx",
        question="q",
        intent="conceptual",
    )
    case = build_answer_prompt(
        system_prompt="sys",
        context="ctx",
        question="q",
        intent="case",
    )
    assert "Modo conceptual" in conceptual
    assert "Modo caso práctico" in case
    assert "ctx" in conceptual
    assert "(vacío)" in build_answer_prompt(
        system_prompt="sys",
        context="  ",
        question="q",
        intent="conceptual",
    )


def test_build_refine_prompt_by_intent():
    conceptual = build_refine_prompt("priorizar", "conceptual")
    case = build_refine_prompt("priorizar features", "case")
    assert "definición" in conceptual
    assert "caso" in case
    assert "priorizar features" in case


def test_fallback_message_uses_display_name(clean_domain_env):
    domain = get_domain()
    msg = fallback_message(domain)
    assert domain.display_name in msg
