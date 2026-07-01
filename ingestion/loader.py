"""
Unified document loader.
Supports PDF, TXT, and Markdown files using LangChain loaders.
"""
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import logging

logger = logging.getLogger(__name__)

def load_documents(file_path: Path) -> List[Document]:
    """
    Loads a single file and returns a list of Documents.
    Supports .pdf, .txt, .md extensions.
    """
    suffix = file_path.suffix.lower()
    logger.info(f"Loading {file_path} with suffix {suffix}")

    if suffix == ".pdf":
        loader = PyPDFLoader(str(file_path))
    elif suffix in (".txt", ".md", ".markdown"):
        # TextLoader works well for text and markdown.
        loader = TextLoader(str(file_path), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    return loader.load()