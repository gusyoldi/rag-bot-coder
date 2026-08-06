"""Shared domain configuration model."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class DomainConfig:
    """Business identity and knobs for one coach domain."""

    id: str
    display_name: str
    tagline: str
    corpus_dir: Path
    exit_commands: frozenset[str] = frozenset({"exit", "salir"})
    system_prompt: str = ""
    tools: list[str] = field(default_factory=list)
