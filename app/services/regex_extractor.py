import re
from typing import Dict, Optional

from app.domain.models import TARGET_FIELDS


class RegexExtractor:
    def __init__(self) -> None:
        self.patterns = {
            "Mahal_Kodu": re.compile(r"Mahal[\s_-]?Kodu[:\s]+(?P<value>\w+)", re.IGNORECASE),
            "M2": re.compile(r"(?P<value>\d+(?:[,.]\d+)?)\s*m2", re.IGNORECASE),
            "Asgari_Kira": re.compile(r"Asgari\s+Kira[:\s]+(?P<value>[\d.,]+)", re.IGNORECASE),
            "Ciro_Kira_Orani": re.compile(r"Ciro\s+Kira\s+Orani[:\s]+(?P<value>[\d.,]+%?)", re.IGNORECASE),
            "Dekorasyon_Koordinasyon": re.compile(
                r"Dekorasyon\s+Koordinasyon[:\s]+(?P<value>[\w\s]+)", re.IGNORECASE
            ),
            "Mali_Sorumluluk_Sigortasi": re.compile(
                r"Mali\s+Sorumluluk\s+Sigortasi[:\s]+(?P<value>[\w\s]+)", re.IGNORECASE
            ),
            "Gecikme_Faizi": re.compile(r"Gecikme\s+Faizi[:\s]+(?P<value>[\d.,]+%?)", re.IGNORECASE),
            "Bir_Yil_Uzama_Artis": re.compile(
                r"Bir\s+Yil\s+Uzama\s+Artis[:\s]+(?P<value>[\d.,]+%?)", re.IGNORECASE
            ),
            "Bir_Yil_Uzama_Ciro_Kira": re.compile(
                r"Bir\s+Yil\s+Uzama\s+Ciro\s+Kira[:\s]+(?P<value>[\d.,]+%?)",
                re.IGNORECASE,
            ),
            "Ceza_Bedeli": re.compile(r"Ceza\s+Bedeli[:\s]+(?P<value>[\d.,]+)", re.IGNORECASE),
        }

    def extract(self, text: str) -> Dict[str, Optional[str]]:
        results: Dict[str, Optional[str]] = {field: None for field in TARGET_FIELDS}
        for key, pattern in self.patterns.items():
            match = pattern.search(text)
            if match:
                results[key] = match.group("value").strip()
        return results
