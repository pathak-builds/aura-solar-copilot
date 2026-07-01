"""
Orchestrates the full ingestion pipeline:
Scan data/manuals -> Load -> Split -> Embed -> Store in ChromaDB
Run as: python -m ingestion.ingest
"""
import logging
from pathlib import Path
from ingestion.loader import load_documents
from ingestion.splitter import split_documents
from rag.embedder import get_embedder
from rag.vector_store import get_vector_store
from config import settings

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

def run_ingestion():
    manuals_dir = settings.data_dir / "manuals"
    if not manuals_dir.exists():
        logger.error(f"Manuals directory not found: {manuals_dir}")
        return

    # Discover all supported files
    files = []
    for ext in ["*.pdf", "*.txt", "*.md"]:
        files.extend(manuals_dir.glob(ext))

    if not files:
        logger.warning("No documents found to ingest.")
        return

    logger.info(f"Found {len(files)} files. Starting ingestion...")

    all_docs = []
    for file_path in files:
        try:
            docs = load_documents(file_path)
            # Tag each document with source filename for citation
            for d in docs:
                d.metadata["source"] = file_path.name
            all_docs.extend(docs)
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")

    if not all_docs:
        logger.error("No documents loaded. Aborting.")
        return

    logger.info(f"Loaded {len(all_docs)} documents total.")

    # Split
    chunks = split_documents(all_docs)
    logger.info(f"Created {len(chunks)} chunks.")

    # Embed and store
    embedder = get_embedder()
    vector_store = get_vector_store(embedder)
    vector_store.add_documents(chunks)
    logger.info("Ingestion complete. Documents stored in ChromaDB.")

if __name__ == "__main__":
    run_ingestion()