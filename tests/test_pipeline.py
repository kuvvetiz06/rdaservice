from typing import Dict, Optional

from app.domain.models import ExtractionResult
from app.services.merger import ResultMerger
from app.services.pipeline import ExtractionPipeline
from app.services.regex_extractor import RegexExtractor
from app.services.text_extractor import TextExtractor
from app.services.ocr.base import OCREngine
from app.services.llm.base import LLMClient


class DummyOCREngine(OCREngine):
    def extract_text(self, file_bytes: bytes) -> str:
        return "Mahal Kodu: OCR123\nAsgari Kira: 5000"


class DummyLLMClient(LLMClient):
    def generate_fields(
        self, raw_text: str, existing_fields: Dict[str, Optional[str]]
    ) -> Dict[str, Optional[str]]:
        return {"M2": "120", "Ciro_Kira_Orani": "8%"}


def test_pipeline_merges_regex_and_llm_results():
    pipeline = ExtractionPipeline(
        text_extractor=TextExtractor(),
        ocr_engine=DummyOCREngine(),
        regex_extractor=RegexExtractor(),
        llm_client=DummyLLMClient(),
        merger=ResultMerger(),
    )

    result: ExtractionResult = pipeline.run(b"", filename="contract.pdf")

    assert result.fields["Mahal_Kodu"] == "OCR123"
    assert result.fields["Asgari_Kira"] == "5000"
    assert result.fields["M2"] == "120"
    assert result.fields["Ciro_Kira_Orani"] == "8%"
