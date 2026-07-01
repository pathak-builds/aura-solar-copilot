"""
ChromaDB vector store abstraction.
Ensures persistent storage and simple interface.
"""
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from config import settings
import logging
import os

logger = logging.getLogger(__name__)

def get_vector_store(embedder: Embeddings) -> Chroma:
    """
    Returns a Chroma instance connected to the persistent directory.
    If the directory doesn't exist, it will be created.
    """
    persist_dir = settings.chroma_persist_dir
    os.makedirs(persist_dir, exist_ok=True)
    logger.info(f"Connecting to ChromaDB at {persist_dir}")
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=embedder,
        collection_name="solar_manuals",
    )