from __future__ import annotations

from typing import Protocol

import numpy as np


class IOcrEngine(Protocol):
    """Protocol describing OCR engines."""

    def run(self, image: np.ndarray) -> tuple[str, float]:
        """Run OCR on a BGR image and return text with average confidence."""

