from pathlib import Path
from ingestion.loader import load_documents
from ingestion.splitter import split_documents  # adjust path if needed


def test_split_documents_basic():
    file_path = Path("data/manuals/Anchor_Cable_and_Mooring_Line_Inspection.txt")

    docs = load_documents(file_path)
    chunks = split_documents(docs, chunk_size=200, chunk_overlap=50)

    # Basic structure checks
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(hasattr(c, "page_content") for c in chunks)


def test_chunking_behavior():
    file_path = Path("data/manuals/Anchor_Cable_and_Mooring_Line_Inspection.txt")

    docs = load_documents(file_path)

    chunks = split_documents(docs, chunk_size=200, chunk_overlap=50)

    # Ensure splitting actually happened (usually true for long docs)
    original_text = docs[0].page_content
    chunk_text = chunks[0].page_content

    assert len(chunk_text) < len(original_text)


def test_metadata_preserved():
    file_path = Path("data/manuals/Anchor_Cable_and_Mooring_Line_Inspection.txt")

    docs = load_documents(file_path)
    chunks = split_documents(docs, chunk_size=200, chunk_overlap=50)

    # Metadata should exist
    for chunk in chunks:
        assert isinstance(chunk.metadata, dict)
        assert "start_index" in chunk.metadata  # because add_start_index=True