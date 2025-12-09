from typing import Dict, Optional


class ResultMerger:
    @staticmethod
    def merge(
        regex_fields: Dict[str, Optional[str]],
        llm_fields: Dict[str, Optional[str]],
    ) -> Dict[str, Optional[str]]:
        merged = dict(regex_fields)
        for key, value in llm_fields.items():
            if merged.get(key) in (None, "") and value not in (None, ""):
                merged[key] = value
        return merged
