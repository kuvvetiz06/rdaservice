from typing import Literal, Optional

from pydantic import BaseModel


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


class FieldResult(BaseModel):
    name: str
    value: Optional[str]
    confidence: float
    source_quote: Optional[str]
    source: Literal["regex", "llm", "merged"]


class ExtractionResult(BaseModel):
    document_type: str
    ocr_engine: Optional[str]
    ocr_confidence: Optional[float]
    fields: list[FieldResult]
    raw_text: str
