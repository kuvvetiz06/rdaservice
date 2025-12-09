from __future__ import annotations

from typing import Protocol


class ILlmClient(Protocol):
    def extract_fields(self, raw_text: str, document_type: str) -> dict:
        """Extract structured fields from raw text."""

