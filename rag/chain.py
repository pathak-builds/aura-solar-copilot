"""
High-level convenience functions for the RAG system.
"""
from rag.retriever import Retriever
from rag.vector_store import get_vector_store
from rag.embedder import get_embedder
from config import settings

def build_retriever() -> Retriever:
    """
    Creates and returns a ready-to-use Retriever instance.
    """
    embedder = get_embedder()
    vector_store = get_vector_store(embedder)
    return Retriever(vector_store)

def retrieve_context(query: str, top_k: int = None) -> tuple[list, str]:
    """
    Convenience function: retrieves documents and their formatted sources.
    Returns (documents_list, sources_string).
    """
    if top_k is None:
        top_k = settings.top_k_docs
    retriever = build_retriever()
    docs = retriever.retrieve(query, top_k)
    sources = retriever.format_sources(docs)
    return docs, sources