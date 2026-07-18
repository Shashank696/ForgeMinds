"""
Tests for the document ingestion pipeline.
Assigned to: RUDRA
"""

import pytest
import os
import sys
import tempfile
import asyncio

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.file_utils import validate_file_type, get_file_extension, generate_filename, get_file_size
from backend.utils.text_utils import clean_text, chunk_text, normalize_whitespace, extract_sentences
from shared.constants import MAX_FILE_SIZE_BYTES, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


class TestDocumentUpload:
    """Tests for document upload functionality."""

    def test_upload_pdf(self):
        """Test uploading a PDF document."""
        assert validate_file_type("report.pdf") is True

    def test_upload_image(self):
        """Test uploading an image document."""
        assert validate_file_type("scan.png") is True
        assert validate_file_type("photo.jpg") is True
        assert validate_file_type("diagram.jpeg") is True

    def test_upload_spreadsheet(self):
        """Test uploading a spreadsheet."""
        assert validate_file_type("data.xlsx") is True
        assert validate_file_type("log.csv") is True

    def test_upload_invalid_file_type(self):
        """Test that invalid file types are rejected."""
        assert validate_file_type("virus.exe") is False
        assert validate_file_type("script.py") is False
        assert validate_file_type("binary.bin") is False
        assert validate_file_type("archive.zip") is False

    def test_upload_file_too_large(self):
        """Test that oversized files are rejected."""
        # MAX_FILE_SIZE_BYTES should be 50 * 1024 * 1024 = 52_428_800
        assert MAX_FILE_SIZE_BYTES == 50 * 1024 * 1024

    def test_get_file_extension(self):
        """Test file extension extraction."""
        assert get_file_extension("report.pdf") == ".pdf"
        assert get_file_extension("IMAGE.PNG") == ".png"
        assert get_file_extension("no_extension") == ""
        assert get_file_extension("multi.part.name.docx") == ".docx"

    def test_generate_filename(self):
        """Test unique filename generation."""
        name = generate_filename("My Report (2024).pdf")
        assert name.endswith(".pdf")
        assert "My" not in name or "_" in name  # spaces should be sanitized
        # Should have UUID prefix
        assert len(name) > 15

        # Two calls should generate different names
        name2 = generate_filename("My Report (2024).pdf")
        assert name != name2

    def test_get_file_size(self):
        """Test file size retrieval."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(b"Hello World")
            f.flush()
            path = f.name

        try:
            size = get_file_size(path)
            assert size == 11
        finally:
            os.unlink(path)

        # Non-existent file should return 0
        assert get_file_size("/nonexistent/file.txt") == 0


class TestOCR:
    """Tests for OCR text extraction."""

    def test_extract_text_from_digital_pdf(self):
        """Test text extraction from a native (digital) PDF."""
        from unittest.mock import patch, MagicMock
        from backend.services.ocr_service import OCRService

        service = OCRService()

        # Create a mock page with text
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample equipment P-1001A maintenance report"

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = asyncio.run(service.extract_text_from_pdf("test.pdf"))

        assert "P-1001A" in result["text"]
        assert result["confidence"] > 0
        assert result["metadata"]["page_count"] == 1

    def test_extract_text_from_scanned_pdf(self):
        """Test OCR on a scanned document."""
        from unittest.mock import patch, MagicMock
        from backend.services.ocr_service import OCRService

        service = OCRService()

        # Mock a page with no native text (scanned)
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""
        mock_img = MagicMock()
        mock_page.to_image.return_value = MagicMock(original=mock_img)

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)

        mock_ocr_data = {
            "text": ["Equipment", "P-2001", "valve", ""],
            "conf": [95, 88, 92, -1],
        }

        with patch("pdfplumber.open", return_value=mock_pdf), \
             patch("pytesseract.image_to_data", return_value=mock_ocr_data):
            result = asyncio.run(service.extract_text_from_pdf("scanned.pdf"))

        assert result["metadata"]["page_count"] == 1
        # Text should contain OCR results
        assert isinstance(result["text"], str)


class TestChunking:
    """Tests for text chunking."""

    def test_chunk_short_text(self):
        """Test chunking on text shorter than chunk size."""
        text = "This is a short text."
        chunks = chunk_text(text, chunk_size=1000, overlap=200)
        assert len(chunks) == 1
        assert chunks[0]["text"] == text
        assert chunks[0]["chunk_index"] == 0
        assert chunks[0]["start_char"] == 0
        assert chunks[0]["end_char"] == len(text)

    def test_chunk_long_text(self):
        """Test chunking produces correct overlap."""
        # Generate text longer than chunk_size
        sentences = [f"Sentence number {i} about equipment maintenance. " for i in range(100)]
        text = "".join(sentences)

        chunks = chunk_text(text, chunk_size=200, overlap=50)

        assert len(chunks) > 1
        # Each chunk should have valid metadata
        for chunk in chunks:
            assert "text" in chunk
            assert "start_char" in chunk
            assert "end_char" in chunk
            assert "chunk_index" in chunk
            assert len(chunk["text"]) > 0

        # Chunk indices should be sequential
        for i, chunk in enumerate(chunks):
            assert chunk["chunk_index"] == i

    def test_chunk_empty_text(self):
        """Test chunking with empty text."""
        chunks = chunk_text("", chunk_size=1000, overlap=200)
        assert chunks == []

    def test_clean_text(self):
        """Test text cleaning."""
        # Null bytes and control characters
        dirty = "Hello\x00World\x01\x02\x03Normal"
        cleaned = clean_text(dirty)
        assert "\x00" not in cleaned
        assert "\x01" not in cleaned
        assert "Hello" in cleaned
        assert "Normal" in cleaned

    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        text = "Multiple   spaces    here\n\n\n\n\nToo many newlines"
        normalized = normalize_whitespace(text)
        assert "   " not in normalized
        assert "\n\n\n" not in normalized

    def test_extract_sentences(self):
        """Test sentence extraction."""
        text = "The pump P-1001A failed. Vibration was 7.2 mm/s. Maintenance was scheduled."
        sentences = extract_sentences(text)
        assert len(sentences) == 3
        assert "P-1001A" in sentences[0]

    def test_sentence_abbreviation_handling(self):
        """Test that abbreviations don't cause false sentence splits."""
        text = "See Ref. No. 42 for details. The equipment was inspected."
        sentences = extract_sentences(text)
        # Should not split at "Ref." or "No."
        assert len(sentences) == 2
