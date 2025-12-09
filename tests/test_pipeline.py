from typing import Dict, Optional

from app.domain.models import ExtractionResult
from app.services.merger import ResultMerger
from app.services.pipeline import ExtractionPipeline
from app.services.regex_extractor import RegexExtractor
from app.services.text_extractor import TextExtractor
from app.services.ocr.base import IOcrEngine
from app.services.llm.base import LLMClient


class DummyOCREngine(IOcrEngine):
    def run(self, image):  # type: ignore[override]
        return "Mahal Kodu: OCR123\nAsgari Kira: 5000", 0.9


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
    field_map = {field.name: field for field in result.fields}

    assert result.document_type == "contract.pdf"
    assert result.ocr_engine == "DummyOCREngine"
    assert field_map["Mahal_Kodu"].value == "OCR123"
    assert field_map["Asgari_Kira"].value == "5000"
    assert field_map["M2"].value == "120"
    assert field_map["Ciro_Kira_Orani"].value == "8%"
