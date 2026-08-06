"""Tests for corpus loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.ingestion.loader import load_corpus


def test_load_corpus_reads_markdown(tmp_corpus: Path):
    docs = load_corpus(tmp_corpus)
    assert len(docs) == 1
    assert "RICE" in docs[0].page_content
    assert docs[0].metadata["source"] == "rice.md"


def test_load_corpus_missing_dir(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_corpus(tmp_path / "missing")


def test_load_corpus_no_markdown(tmp_path: Path):
    empty = tmp_path / "empty"
    empty.mkdir()
    (empty / "notes.txt").write_text("not markdown", encoding="utf-8")
    with pytest.raises(ValueError, match="No markdown"):
        load_corpus(empty)
