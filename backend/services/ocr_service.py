"""
ForgeMinds — OCR / Text Extraction Service.
Modular OCR with pdfplumber, pytesseract, python-docx, and pandas.
Assigned to: RUDRA
"""

import asyncio
import os
from typing import Dict, Any, List

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class OCRService:
    """Handles text extraction from varied sources. Assigned to: RUDRA"""

    def __init__(self):
        self.logger = get_logger(__name__)

    # ──────────────────────────────────────────────
    # Public dispatcher
    # ──────────────────────────────────────────────

    async def extract_text(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Route to the appropriate extractor based on file_type.

        Returns:
            {text, confidence, pages, metadata}
        """
        ft = file_type.lower().lstrip(".")
        extractors = {
            "pdf": self.extract_text_from_pdf,
            "png": self.extract_text_from_image,
            "jpg": self.extract_text_from_image,
            "jpeg": self.extract_text_from_image,
            "tiff": self.extract_text_from_image,
            "tif": self.extract_text_from_image,
            "docx": self.extract_text_from_docx,
            "doc": self.extract_text_from_docx,
            "txt": self.extract_text_from_txt,
            "csv": self.extract_text_from_spreadsheet,
            "xlsx": self.extract_text_from_spreadsheet,
            "xls": self.extract_text_from_spreadsheet,
        }
        extractor = extractors.get(ft)
        if extractor is None:
            self.logger.warning("No extractor for file type '%s', trying plain text", ft)
            extractor = self.extract_text_from_txt

        self.logger.info("Extracting text from %s (type=%s)", file_path, ft)
        return await extractor(file_path)

    # ──────────────────────────────────────────────
    # PDF extraction
    # ──────────────────────────────────────────────

    async def extract_text_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text from a PDF document using pdfplumber, with pytesseract fallback."""

        def _extract_sync():
            import pdfplumber

            pages_data: List[Dict[str, Any]] = []
            full_text_parts: List[str] = []
            total_confidence = 0.0
            page_count = 0

            try:
                with pdfplumber.open(file_path) as pdf:
                    page_count = len(pdf.pages)
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text() or ""
                        confidence = 1.0  # native text = high confidence

                        if not page_text.strip():
                            # Scanned page — attempt OCR via pytesseract
                            page_text, confidence = self._ocr_pdf_page(page)

                        pages_data.append({
                            "page_number": i + 1,
                            "text": page_text,
                            "confidence": confidence,
                        })
                        full_text_parts.append(page_text)
                        total_confidence += confidence
            except Exception as exc:
                logger.error("pdfplumber failed on %s: %s", file_path, exc)
                raise

            avg_conf = total_confidence / max(page_count, 1)
            return {
                "text": "\n\n".join(full_text_parts),
                "confidence": round(avg_conf, 3),
                "pages": pages_data,
                "metadata": {
                    "page_count": page_count,
                    "method": "pdfplumber+tesseract",
                },
            }

        return await asyncio.to_thread(_extract_sync)

    def _ocr_pdf_page(self, page) -> tuple:
        """OCR a single pdfplumber page that has no native text."""
        try:
            import pytesseract
            from PIL import Image

            img = page.to_image(resolution=300).original
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            words = [w for w in data["text"] if w.strip()]
            confs = [
                int(c) for c, w in zip(data["conf"], data["text"])
                if w.strip() and str(c).lstrip("-").isdigit() and int(c) > 0
            ]
            text = " ".join(words)
            confidence = (sum(confs) / len(confs) / 100.0) if confs else 0.0
            return text, round(confidence, 3)
        except Exception as exc:
            logger.warning("OCR fallback failed for page: %s", exc)
            return "", 0.0

    # ──────────────────────────────────────────────
    # Image extraction
    # ──────────────────────────────────────────────

    async def extract_text_from_image(self, file_path: str) -> Dict[str, Any]:
        """Extract text from an image using pytesseract."""

        def _extract_sync():
            import pytesseract
            from PIL import Image

            try:
                img = Image.open(file_path)
                # Get detailed data with confidence scores
                data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                words = [w for w in data["text"] if w.strip()]
                confs = [
                    int(c) for c, w in zip(data["conf"], data["text"])
                    if w.strip() and str(c).lstrip("-").isdigit() and int(c) > 0
                ]
                text = " ".join(words)
                confidence = (sum(confs) / len(confs) / 100.0) if confs else 0.0
            except Exception as exc:
                logger.error("pytesseract failed on %s: %s", file_path, exc)
                raise

            return {
                "text": text,
                "confidence": round(confidence, 3),
                "pages": [{"page_number": 1, "text": text, "confidence": round(confidence, 3)}],
                "metadata": {"method": "tesseract"},
            }

        return await asyncio.to_thread(_extract_sync)

    # ──────────────────────────────────────────────
    # DOCX extraction
    # ──────────────────────────────────────────────

    async def extract_text_from_docx(self, file_path: str) -> Dict[str, Any]:
        """Extract text from DOCX using python-docx."""

        def _extract_sync():
            from docx import Document as DocxDocument

            try:
                doc = DocxDocument(file_path)
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                text = "\n\n".join(paragraphs)
            except Exception as exc:
                logger.error("python-docx failed on %s: %s", file_path, exc)
                raise

            return {
                "text": text,
                "confidence": 1.0,
                "pages": [],
                "metadata": {
                    "method": "python-docx",
                    "paragraph_count": len(paragraphs),
                },
            }

        return await asyncio.to_thread(_extract_sync)

    # ──────────────────────────────────────────────
    # Plain text extraction
    # ──────────────────────────────────────────────

    async def extract_text_from_txt(self, file_path: str) -> Dict[str, Any]:
        """Extract text from a plain text file."""

        def _extract_sync():
            text = ""
            for encoding in ("utf-8", "latin-1", "cp1252"):
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        text = f.read()
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue

            return {
                "text": text,
                "confidence": 1.0,
                "pages": [],
                "metadata": {"method": "direct_read"},
            }

        return await asyncio.to_thread(_extract_sync)

    # ──────────────────────────────────────────────
    # Spreadsheet extraction
    # ──────────────────────────────────────────────

    async def extract_text_from_spreadsheet(self, file_path: str) -> Dict[str, Any]:
        """Extract text from Excel/CSV using pandas."""

        def _extract_sync():
            import pandas as pd

            ext = os.path.splitext(file_path)[1].lower()
            text_parts: List[str] = []
            sheet_count = 0

            try:
                if ext == ".csv":
                    df = pd.read_csv(file_path)
                    text_parts.append(df.to_string(index=False))
                    sheet_count = 1
                else:
                    xls = pd.ExcelFile(file_path)
                    sheet_count = len(xls.sheet_names)
                    for sheet_name in xls.sheet_names:
                        df = pd.read_excel(xls, sheet_name=sheet_name)
                        text_parts.append(f"=== Sheet: {sheet_name} ===\n{df.to_string(index=False)}")
            except Exception as exc:
                logger.error("Spreadsheet extraction failed for %s: %s", file_path, exc)
                raise

            return {
                "text": "\n\n".join(text_parts),
                "confidence": 1.0,
                "pages": [],
                "metadata": {"method": "pandas", "sheet_count": sheet_count},
            }

        return await asyncio.to_thread(_extract_sync)
