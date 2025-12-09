from typing import Any

from app.services.ocr.base import IOcrEngine


class PaddleOCREngine(IOcrEngine):  # pragma: no cover - placeholder
    def run(self, image: Any) -> tuple[str, float]:  # type: ignore[override]
        """Placeholder for future PaddleOCR integration."""
        return "", 0.0
