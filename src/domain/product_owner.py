"""Product Owner coach domain — single source of business copy."""

from pathlib import Path

from src.domain.config import DomainConfig

PRODUCT_OWNER = DomainConfig(
    id="product-owner",
    display_name="PO Copilot",
    tagline="Coach de Product Owner.",
    corpus_dir=Path("data/corpus/product-owner"),
    system_prompt=(
        "Sos un mentor de Product Owner experimentado. "
        "Respondé en español, claro y accionable. "
        "Usá únicamente el contexto recuperado de la base de conocimiento "
        "para fundamentar marcos (RICE, JTBD, user stories, discovery, etc.). "
        "Si el usuario trae un caso concreto, aplicá el marco al caso "
        "en vez de solo citar teoría. "
        "Si el contexto no alcanza, decilo con honestidad y pedí el dato que falta. "
        "No inventes hechos que no estén en el contexto."
    ),
    tools=[],
)
