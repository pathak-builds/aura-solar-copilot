"""
Embedding model abstraction.
Uses LangChain's HuggingFaceEmbeddings to easily swap models.
"""
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import settings
import logging

logger = logging.getLogger(__name__)

def get_embedder() -> HuggingFaceEmbeddings:
    """
    Returns an embedder instance configured with the model from settings.
    """
    logger.info(f"Loading embedding model: {settings.embedding_model_name}")
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model_name,
        model_kwargs={"device": "cpu"},  # use 'cuda' if GPU available
        encode_kwargs={"normalize_embeddings": True},
    )