"""Resolve the active domain from an id or DOMAIN_ID env var."""

from __future__ import annotations

import os

from src.domain.config import DomainConfig
from src.domain.product_owner import PRODUCT_OWNER

_DOMAINS: dict[str, DomainConfig] = {
    PRODUCT_OWNER.id: PRODUCT_OWNER,
}

_DEFAULT_DOMAIN_ID = PRODUCT_OWNER.id


def get_domain(domain_id: str | None = None) -> DomainConfig:
    """Return the domain config for ``domain_id`` or ``DOMAIN_ID`` / default."""
    resolved = domain_id or os.getenv("DOMAIN_ID") or _DEFAULT_DOMAIN_ID
    try:
        return _DOMAINS[resolved]
    except KeyError as exc:
        known = ", ".join(sorted(_DOMAINS))
        raise ValueError(
            f"Unknown domain id '{resolved}'. Known domains: {known}"
        ) from exc
