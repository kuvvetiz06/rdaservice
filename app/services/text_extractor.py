from __future__ import annotations

import io
import logging
from typing import Optional

try:
    import pdfplumber
except ImportError:  # pragma: no cover - optional dependency guard
    pdfplumber = None

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - optional dependency guard
    PdfReader = None
from app.services.ocr.base import OCREngine


LOGGER = logging.getLogger(__name__)


class TextExtractor:
    """Extract text from PDF or image-like files using native layers and OCR."""

    KEYWORDS = ["kira", "kiracı", "kiralayan", "tl", "mahal"]

    def __init__(self, ocr_engine: Optional[OCREngine] = None) -> None:
        self.ocr_engine = ocr_engine

    @staticmethod
    def _extract_pdfplumber(file_obj: io.BytesIO) -> str:
        if not pdfplumber:
            return ""
        try:
            with pdfplumber.open(file_obj) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as exc:  # pragma: no cover - library level issues
            LOGGER.warning("pdfplumber failed to extract text: %s", exc)
            return ""

    @staticmethod
    def _extract_pypdf(file_obj: io.BytesIO) -> str:
        if not PdfReader:
            return ""
        try:
            reader = PdfReader(file_obj)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:  # pragma: no cover - library level issues
            LOGGER.warning("PyPDF failed to extract text: %s", exc)
            return ""

    @staticmethod
    def _decode_text(file_bytes: bytes) -> str:
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return file_bytes.decode("latin-1")
            except UnicodeDecodeError:
                return ""

    def _is_native_valid(self, text: str) -> bool:
        content = text.strip().lower()
        if len(content) < 80:
            return False
        return any(keyword in content for keyword in self.KEYWORDS)

    def _extract_via_ocr(self, file_bytes: bytes) -> tuple[str, Optional[float], str]:
        if not self.ocr_engine:
            LOGGER.warning("OCR engine is not configured; returning empty text from OCR fallback")
            return "", None, "ocr"
        text = self.ocr_engine.extract_text(file_bytes)
        confidence = getattr(self.ocr_engine, "confidence", None)
        return text, confidence, "ocr"

    def extract_text(self, file_bytes: bytes, document_type: str) -> tuple[str, Optional[float], str]:
        extension = (document_type or "").lower()

        if not file_bytes:
            if extension.endswith(".txt") or extension.endswith(".md"):
                return "", None, "native"
            return self._extract_via_ocr(file_bytes)

        if extension.endswith(".txt") or extension.endswith(".md"):
            return self._decode_text(file_bytes), None, "native"

        if extension.endswith(".pdf"):
            buffer = io.BytesIO(file_bytes)
            text = self._extract_pdfplumber(buffer)
            if not text:
                buffer.seek(0)
                text = self._extract_pypdf(buffer)

            if text and self._is_native_valid(text):
                return text, None, "native"

            return self._extract_via_ocr(file_bytes)

        # For image-like inputs, rely on OCR directly
        return self._extract_via_ocr(file_bytes)
