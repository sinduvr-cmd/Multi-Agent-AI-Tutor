"""
Test Suite: PDF Processing and Ingestion.
Verifies PyMuPDF extraction, layout chunks, and topic hierarchy detection.
"""

import os
from pathlib import Path
from services.pdf_processor import PDFProcessor

SAMPLE_PDF = Path(__file__).resolve().parent.parent / "sample_data" / "ncert_class6_perimeter_and_area.pdf"


def test_pdf_extraction_basic():
    processor = PDFProcessor()
    analysis, chunks = processor.process_pdf(str(SAMPLE_PDF), "ncert_class6_perimeter_and_area.pdf")

    assert analysis["title"] == "Perimeter and Area"
    assert analysis["subject"] == "Mathematics"
    assert analysis["total_pages"] >= 2
    assert analysis["confidence_score"] > 0.8
    assert len(chunks) > 5
    assert len(analysis["topics"]) >= 2


def test_chunk_types_and_metadata():
    processor = PDFProcessor()
    analysis, chunks = processor.process_pdf(str(SAMPLE_PDF), "ncert_class6_perimeter_and_area.pdf")

    chunk_types = {c["chunk_type"] for c in chunks}
    assert "text" in chunk_types

    for c in chunks:
        assert "chunk_id" in c
        assert "document_id" in c
        assert c["page_number"] >= 1
        assert len(c["content"]) > 0
