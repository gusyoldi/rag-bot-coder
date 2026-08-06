"""Load markdown corpus files from a domain corpus directory."""

from pathlib import Path

from langchain_core.documents import Document


def load_corpus(corpus_dir: Path) -> list[Document]:
    """Load all ``.md`` files under ``corpus_dir`` as LangChain documents."""
    if not corpus_dir.is_dir():
        raise FileNotFoundError(f"Corpus directory not found: {corpus_dir}")

    documents: list[Document] = []
    for path in sorted(corpus_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        documents.append(
            Document(
                page_content=text,
                metadata={"source": path.name, "path": str(path)},
            )
        )

    if not documents:
        raise ValueError(f"No markdown documents found in {corpus_dir}")

    return documents
