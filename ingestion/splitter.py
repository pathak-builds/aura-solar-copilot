"""
Document splitting using RecursiveCharacterTextSplitter.
Configured for technical manuals.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
import logging

logger = logging.getLogger(__name__)

def split_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Document]:
    """
    Splits a list of documents into smaller chunks.
    """
    logger.info(f"Splitting {len(documents)} documents with chunk_size={chunk_size}, overlap={chunk_overlap}")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,  # tracks original position
    )
    return splitter.split_documents(documents)