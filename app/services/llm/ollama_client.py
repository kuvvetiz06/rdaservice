from __future__ import annotations

import json
import logging
from typing import Dict, Optional

import requests

from app.core.config import get_settings
from app.services.llm.base import ILlmClient


LOGGER = logging.getLogger(__name__)


TARGET_FIELDS = [
    "Mahal_Kodu",
    "M2",
    "Asgari_Kira",
    "Ciro_Kira_Orani",
    "Dekorasyon_Koordinasyon",
    "Mali_Sorumluluk_Sigortasi",
    "Gecikme_Faizi",
    "Bir_Yil_Uzama_Artis",
    "Bir_Yil_Uzama_Ciro_Kira",
    "Ceza_Bedeli",
]


class OllamaLlmClient(ILlmClient):
    def __init__(self, model: Optional[str] = None, endpoint: Optional[str] = None) -> None:
        settings = get_settings()
        self.model = model or settings.ollama_model
        self.endpoint = endpoint or settings.ollama_base_url

    def _build_prompt(self, raw_text: str, document_type: str) -> str:
        fields = ", ".join(TARGET_FIELDS)
        return (
            "Aşağıdaki metinden belirtilen alanları JSON olarak çıkar.\n"
            f"Belge tipi: {document_type or 'kira sözleşmesi'}\n"
            f"Çıkarılacak alanlar: {fields}\n"
            "Her alan için şu JSON formatında cevap ver:\n"
            '{"value": "...", "confidence": 0-1, "source_quote": "..."}\n\n'
            f"Metin:\n{raw_text}"
        )

    def extract_fields(self, raw_text: str, document_type: str) -> Dict[str, dict]:
        prompt = self._build_prompt(raw_text, document_type or "kira sözleşmesi")
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            response = requests.post(
                f"{self.endpoint}/api/generate", json=payload, timeout=30
            )
            response.raise_for_status()
            parsed_response = json.loads(response.text)
            llm_output = parsed_response.get("response", parsed_response)
            if isinstance(llm_output, str):
                llm_output = json.loads(llm_output)
            if not isinstance(llm_output, dict):
                return {}
            return {
                field: llm_output.get(field, {})
                for field in TARGET_FIELDS
                if isinstance(llm_output.get(field, {}), dict)
            }
        except Exception as exc:  # pragma: no cover - external dependency
            LOGGER.warning("Ollama request failed: %s", exc)
            return {}

