from __future__ import annotations

import logging
from typing import Optional

import cv2
import numpy as np
from PIL import Image
import pytesseract

from app.core.config import get_settings
from app.services.ocr.base import IOcrEngine


LOGGER = logging.getLogger(__name__)


class TesseractOcrEngine(IOcrEngine):
    def __init__(self, language: Optional[str] = None, resize_max_dim: Optional[int] = None) -> None:
        settings = get_settings()
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
        self.language = language or settings.tesseract_lang
        self.resize_max_dim = resize_max_dim

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if self.resize_max_dim:
            height, width = gray.shape[:2]
            max_dim = max(height, width)
            if max_dim > self.resize_max_dim:
                scale = self.resize_max_dim / float(max_dim)
                new_size = (int(width * scale), int(height * scale))
                gray = cv2.resize(gray, new_size, interpolation=cv2.INTER_CUBIC)
        return gray

    def run(self, image: np.ndarray) -> tuple[str, float]:  # pragma: no cover - requires binary
        try:
            processed = self._preprocess(image)
            pil_image = Image.fromarray(processed)
            data = pytesseract.image_to_data(
                pil_image,
                lang=self.language,
                output_type=pytesseract.Output.DICT,
            )
        except Exception as exc:  # pragma: no cover - library level issues
            LOGGER.warning("Tesseract OCR failed: %s", exc)
            return "", 0.0

        words = [text for text in data.get("text", []) if text.strip()]
        text = " ".join(words).strip()

        confidences = []
        for conf in data.get("conf", []):
            try:
                value = float(conf)
            except (TypeError, ValueError):
                continue
            if value >= 0:
                confidences.append(value)
        avg_confidence = (sum(confidences) / len(confidences) / 100) if confidences else 0.0

        return text, avg_confidence

