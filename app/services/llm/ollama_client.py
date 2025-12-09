from __future__ import annotations

import logging
from typing import Dict, Optional

import requests

from app.core.config import get_settings
from app.services.llm.base import LLMClient


LOGGER = logging.getLogger(__name__)


class OllamaClient(LLMClient):
    def __init__(self, model: Optional[str] = None, endpoint: str = "http://localhost:11434") -> None:
        settings = get_settings()
        self.model = model or settings.ollama_model
        self.endpoint = endpoint

    def _build_prompt(self, raw_text: str, existing_fields: Dict[str, Optional[str]]) -> str:
        missing_fields = [
            name for name, value in existing_fields.items() if value in (None, "")
        ]
        prompt_fields = ", ".join(missing_fields)
        return (
            "You are an extraction assistant. Provided contract text: "
            f"{raw_text}\nReturn JSON with fields: {prompt_fields}"
        )

    def generate_fields(
        self, raw_text: str, existing_fields: Dict[str, Optional[str]]
    ) -> Dict[str, Optional[str]]:  # pragma: no cover - requires Ollama runtime
        prompt = self._build_prompt(raw_text, existing_fields)
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            response = requests.post(f"{self.endpoint}/api/generate", json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("response", {}) if isinstance(data, dict) else {}
        except Exception as exc:
            LOGGER.warning("Ollama request failed: %s", exc)
            return {}
