from app.services.ocr.base import OCREngine


class PaddleOCREngine(OCREngine):  # pragma: no cover - placeholder
    def extract_text(self, file_bytes: bytes) -> str:
        """Placeholder for future PaddleOCR integration."""
        return ""
