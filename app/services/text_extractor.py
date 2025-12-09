from __future__ import annotations

import io
import logging
from typing import Optional

import numpy as np
import cv2

try:
    from pdf2image import convert_from_bytes
except ImportError:  # pragma: no cover - optional dependency guard
    convert_from_bytes = None

try:
    import pdfplumber
except ImportError:  # pragma: no cover - optional dependency guard
    pdfplumber = None

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - optional dependency guard
    PdfReader = None
from app.services.ocr.base import IOcrEngine


LOGGER = logging.getLogger(__name__)


class TextExtractor:
    """Extract text from PDF or image-like files using native layers and OCR."""

    KEYWORDS = ["kira", "kiracı", "kiralayan", "tl", "mahal"]

    def __init__(self, ocr_engine: Optional[IOcrEngine] = None) -> None:
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

    @staticmethod
    def _load_image(file_bytes: bytes) -> Optional[np.ndarray]:
        if not file_bytes:
            return None
        np_bytes = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(np_bytes, cv2.IMREAD_COLOR)
        return image

    @staticmethod
    def _load_pdf_page(file_bytes: bytes, dpi: int = 400) -> Optional[np.ndarray]:
        if not convert_from_bytes:
            LOGGER.warning("pdf2image is not available; skipping OCR fallback for PDF")
            return None
        try:
            pages = convert_from_bytes(file_bytes, dpi=dpi)
        except Exception as exc:  # pragma: no cover - library level issues
            LOGGER.warning("Failed to convert PDF to image for OCR fallback: %s", exc)
            return None
        if not pages:
            return None
        first_page = pages[0].convert("RGB")
        return cv2.cvtColor(np.array(first_page), cv2.COLOR_RGB2BGR)

    def _extract_via_ocr(self, image: Optional[np.ndarray]) -> tuple[str, Optional[float], str]:
        if not self.ocr_engine:
            LOGGER.warning("OCR engine is not configured; returning empty text from OCR fallback")
            return "", None, "ocr"
        if image is None:
            try:
                text, confidence = self.ocr_engine.run(image)
                return text, confidence, "ocr"
            except Exception as exc:  # pragma: no cover - engine-specific behavior
                LOGGER.warning("No image available for OCR fallback; returning empty text: %s", exc)
                return "", None, "ocr"
        text, confidence = self.ocr_engine.run(image)
        return text, confidence, "ocr"

    def extract_text(self, file_bytes: bytes, document_type: str) -> tuple[str, Optional[float], str]:
        extension = (document_type or "").lower()

        if not file_bytes:
            if extension.endswith(".txt") or extension.endswith(".md"):
                return "", None, "native"
            return self._extract_via_ocr(None)

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

            image = self._load_pdf_page(file_bytes)
            return self._extract_via_ocr(image)

        # For image-like inputs, rely on OCR directly
        image = self._load_image(file_bytes)
        return self._extract_via_ocr(image)
