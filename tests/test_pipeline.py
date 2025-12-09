from typing import Dict, Optional

from app.domain.models import ExtractionResult
from app.services.merger import ResultMerger
from app.services import pipeline
from app.services.pipeline import ExtractionPipeline
from app.services.regex_extractor import RegexExtractor
from app.services.text_extractor import TextExtractor
from app.services.ocr.base import IOcrEngine
from app.services.llm.base import ILlmClient


class DummyOCREngine(IOcrEngine):
    def run(self, image):  # type: ignore[override]
        return "Mahal Kodu: OCR123\nAsgari Kira: 5000", 0.9


class DummyLLMClient(ILlmClient):
    def extract_fields(self, raw_text: str, document_type: str) -> Dict[str, dict]:
        return {
            "M2": {"value": "120", "confidence": 0.7, "source_quote": "M2 120"},
            "Ciro_Kira_Orani": {
                "value": "8%",
                "confidence": 0.65,
                "source_quote": "Ciro kira oranı %8",
            },
        }


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
    assert field_map["Mahal_Kodu"].source == "regex"
    assert field_map["Asgari_Kira"].value == "5000"
    assert field_map["Asgari_Kira"].source == "regex"
    assert field_map["M2"].value == "120"
    assert field_map["M2"].source == "llm"
    assert field_map["Ciro_Kira_Orani"].value == "8%"
    assert field_map["Ciro_Kira_Orani"].source == "llm"


def test_run_extraction_smoke(monkeypatch):
    class DummyTesseract:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, image):  # type: ignore[override]
            return "", 0.0

    monkeypatch.setattr(pipeline, "TesseractOcrEngine", DummyTesseract)

    result = pipeline.run_extraction(b"", document_type="empty.pdf")

    assert isinstance(result, ExtractionResult)
    assert result.document_type == "empty.pdf"
    assert result.fields == []
    assert result.raw_text == ""
