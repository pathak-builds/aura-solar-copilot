from pathlib import Path
from ingestion.loader import load_documents


def test_txt_loader():
    file_path = Path("data/manuals/Anchor_Cable_and_Mooring_Line_Inspection.txt")

    docs = load_documents(file_path)

    assert isinstance(docs, list)
    assert len(docs) > 0
    assert docs[0].page_content.strip() != ""


def test_loader_output_structure():
    file_path = Path("data/manuals/Anchor_Cable_and_Mooring_Line_Inspection.txt")

    docs = load_documents(file_path)

    doc = docs[0]

    assert hasattr(doc, "page_content")
    assert hasattr(doc, "metadata")
    assert isinstance(doc.page_content, str)
    assert isinstance(doc.metadata, dict)