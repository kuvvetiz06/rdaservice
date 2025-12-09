from typing import Dict, Optional

from app.domain.models import TARGET_FIELDS


class ResultMerger:
    @staticmethod
    def merge(
        regex_fields: Dict[str, Optional[str]],
        llm_fields: Dict[str, dict],
    ) -> Dict[str, dict]:
        merged: Dict[str, dict] = {}
        for field in TARGET_FIELDS:
            regex_value = regex_fields.get(field)
            llm_value = llm_fields.get(field, {}) if llm_fields else {}
            if regex_value not in (None, ""):
                merged[field] = {
                    "value": regex_value,
                    "confidence": 1.0,
                    "source_quote": None,
                    "source": "regex",
                }
            elif isinstance(llm_value, dict) and llm_value.get("value") not in (None, ""):
                merged[field] = {
                    "value": llm_value.get("value"),
                    "confidence": float(llm_value.get("confidence", 0.0)),
                    "source_quote": llm_value.get("source_quote"),
                    "source": "llm",
                }
            else:
                merged[field] = {
                    "value": None,
                    "confidence": 0.0,
                    "source_quote": None,
                    "source": "merged",
                }
        return merged
