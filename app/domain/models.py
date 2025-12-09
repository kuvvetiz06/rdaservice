from typing import Dict, Optional

from pydantic import BaseModel, Field


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


class ExtractionResult(BaseModel):
    raw_text: str = Field(..., description="Extracted text content")
    fields: Dict[str, Optional[str]] = Field(
        default_factory=dict, description="Structured contract information"
    )


class ExtractionResponse(ExtractionResult):
    """Alias for FastAPI response model."""


class RegexExtractionResult(BaseModel):
    fields: Dict[str, Optional[str]]
