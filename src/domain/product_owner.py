"""Product Owner coach domain — single source of business copy."""

from pathlib import Path

from src.domain.config import DomainConfig

PRODUCT_OWNER = DomainConfig(
    id="product-owner",
    display_name="PO Copilot",
    tagline="Coach de Product Owner.",
    corpus_dir=Path("data/corpus/product-owner"),
    system_prompt="",
    tools=[],
)
