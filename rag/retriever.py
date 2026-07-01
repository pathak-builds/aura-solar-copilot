"""
Retrieval interface.
Provides a clean method to get top-k documents with their metadata.
"""
from langchain_core.documents import Document
from typing import List
from langchain_chroma import Chroma
import logging

logger = logging.getLogger(__name__)

class Retriever:
    """
    Wraps a Chroma vector store to retrieve documents for a query.
    """
    def __init__(self, vector_store: Chroma):
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """
        Performs similarity search and returns documents with source metadata.
        """
        logger.info(f"Retrieving top {top_k} documents for query: '{query[:100]}...'")
        docs = self.vector_store.similarity_search(query, k=top_k)
        logger.info(f"Retrieved {len(docs)} documents")
        return docs

    def format_sources(self, docs: List[Document]) -> str:
        """
        Helper to format retrieved documents as a source citation block.
        """
        sources = []
        for i, doc in enumerate(docs, 1):
            src = doc.metadata.get("source", "unknown")
            snippet = doc.page_content[:150].replace("\n", " ")
            sources.append(f"[{i}] {src}: {snippet}...")
        return "\n".join(sources)