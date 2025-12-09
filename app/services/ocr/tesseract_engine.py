from __future__ import annotations

import io
import logging
from typing import Optional

from PIL import Image
import pytesseract

from app.core.config import get_settings
from app.services.ocr.base import OCREngine


LOGGER = logging.getLogger(__name__)


class TesseractEngine(OCREngine):
    def __init__(self, language: Optional[str] = None) -> None:
        settings = get_settings()
        self.language = language or settings.tesseract_lang

    def extract_text(self, file_bytes: bytes) -> str:  # pragma: no cover - requires binary
        try:
            image = Image.open(io.BytesIO(file_bytes))
        except Exception as exc:
            LOGGER.warning("Unable to open image for OCR: %s", exc)
            return ""

        try:
            return pytesseract.image_to_string(image, lang=self.language)
        except Exception as exc:
            LOGGER.warning("Tesseract OCR failed: %s", exc)
            return ""
