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


LOGGER = logging.getLogger(__name__)


class TextExtractor:
    """Extract text from PDF or image-like files using native layers."""

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

    def extract_text(self, file_bytes: bytes, filename: Optional[str] = None) -> str:
        if not file_bytes:
            return ""

        extension = (filename or "").lower()
        buffer = io.BytesIO(file_bytes)

        if extension.endswith(".pdf"):
            text = self._extract_pdfplumber(buffer)
            if text:
                return text
            buffer.seek(0)
            return self._extract_pypdf(buffer)

        if extension.endswith(".txt") or extension.endswith(".md"):
            return self._decode_text(file_bytes)

        # Fallback: attempt to decode as text
        return self._decode_text(file_bytes)
