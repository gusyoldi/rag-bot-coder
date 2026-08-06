"""Tests for document chunking."""

from __future__ import annotations

from langchain_core.documents import Document

from src.ingestion.chunking import chunk_documents


def test_chunk_documents_splits_long_text():
    text = ("RICE prioritization. " * 80).strip()
    docs = [Document(page_content=text, metadata={"source": "rice.md"})]
    chunks = chunk_documents(docs)
    assert len(chunks) > 1
    assert all(chunk.page_content for chunk in chunks)
    assert all(chunk.metadata.get("source") == "rice.md" for chunk in chunks)


def test_chunk_documents_short_stays_single():
    docs = [Document(page_content="Short note about JTBD.", metadata={"source": "jtbd.md"})]
    chunks = chunk_documents(docs)
    assert len(chunks) == 1
    assert "JTBD" in chunks[0].page_content
