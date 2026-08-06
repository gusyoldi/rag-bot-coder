"""Domain layer — business identity, corpus path, and coach copy."""

from src.domain.config import DomainConfig
from src.domain.registry import get_domain

__all__ = ["DomainConfig", "get_domain"]
