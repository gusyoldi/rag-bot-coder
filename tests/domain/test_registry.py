"""Tests for domain registry resolution."""

from __future__ import annotations

import pytest

from src.domain import get_domain
from src.domain.product_owner import PRODUCT_OWNER


def test_get_domain_default(clean_domain_env):
    domain = get_domain()
    assert domain.id == PRODUCT_OWNER.id
    assert domain.display_name == "PO Copilot"


def test_get_domain_explicit_id(clean_domain_env):
    domain = get_domain("product-owner")
    assert domain.id == "product-owner"


def test_get_domain_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DOMAIN_ID", "product-owner")
    domain = get_domain()
    assert domain.id == "product-owner"


def test_get_domain_unknown_raises(clean_domain_env):
    with pytest.raises(ValueError, match="Unknown domain id"):
        get_domain("does-not-exist")
