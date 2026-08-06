"""Text chunking for corpus documents."""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)


def chunk_documents(documents: list[Document]) -> list[Document]:
    """Split documents into overlapping chunks for embedding."""
    return _SPLITTER.split_documents(documents)
