#!/usr/bin/env python3
"""Ingest the active domain corpus into the local Chroma store."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

# Allow `python scripts/ingest_corpus.py` from repo root.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.domain import get_domain  # noqa: E402
from src.ingestion.chunking import chunk_documents  # noqa: E402
from src.ingestion.loader import load_corpus  # noqa: E402
from src.retrieval.store import collection_count, ingest_documents  # noqa: E402


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Ingest domain corpus into Chroma")
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Corpus directory (default: active domain corpus_dir)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reindex even if the collection already has documents",
    )
    args = parser.parse_args()

    domain = get_domain()
    corpus_dir = args.source or domain.corpus_dir
    if not corpus_dir.is_absolute():
        corpus_dir = ROOT / corpus_dir

    existing = collection_count(domain.id)
    if existing > 0 and not args.force:
        print(
            f"Collection '{domain.id}' already has {existing} vectors. "
            "Skipping (pass --force to reindex)."
        )
        return

    print(f"Loading corpus from {corpus_dir} ...")
    documents = load_corpus(corpus_dir)
    chunks = chunk_documents(documents)
    print(f"Embedding {len(chunks)} chunks into collection '{domain.id}' ...")
    written = ingest_documents(chunks, domain.id, force=args.force)
    print(f"Done. Wrote {written} chunks.")


if __name__ == "__main__":
    main()
