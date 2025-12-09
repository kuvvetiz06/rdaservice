from dataclasses import dataclass
from typing import Optional

from app.domain.models import ExtractionResult, FieldResult
from app.services.ocr.base import IOcrEngine
from app.services.ocr.tesseract_engine import TesseractOcrEngine
from app.services.regex_extractor import RegexExtractor
from app.services.llm.base import ILlmClient
from app.services.llm.ollama_client import OllamaLlmClient
from app.services.merger import ResultMerger
from app.services.text_extractor import TextExtractor


@dataclass
class PipelineDependencies:
    text_extractor: TextExtractor
    ocr_engine: IOcrEngine
    regex_extractor: RegexExtractor
    llm_client: ILlmClient
    merger: ResultMerger


class ExtractionPipeline:
    def __init__(
        self,
        text_extractor: TextExtractor,
        ocr_engine: IOcrEngine,
        regex_extractor: RegexExtractor,
        llm_client: ILlmClient,
        merger: ResultMerger,
    ) -> None:
        self.deps = PipelineDependencies(
            text_extractor=text_extractor,
            ocr_engine=ocr_engine,
            regex_extractor=regex_extractor,
            llm_client=llm_client,
            merger=merger,
        )

        if self.deps.text_extractor.ocr_engine is None:
            self.deps.text_extractor.ocr_engine = self.deps.ocr_engine

    def _extract_text(
        self, file_bytes: bytes, filename: Optional[str]
    ) -> tuple[str, Optional[float], str]:
        return self.deps.text_extractor.extract_text(
            file_bytes, filename or "unknown"
        )

    def run(self, file_bytes: bytes, filename: Optional[str] = None) -> ExtractionResult:
        raw_text, ocr_confidence, source = self._extract_text(file_bytes, filename)
        used_ocr = source == "ocr"
        regex_fields = self.deps.regex_extractor.extract_by_regex(raw_text)
        llm_fields_raw = self.deps.llm_client.extract_fields(
            raw_text, filename or "kira sözleşmesi"
        )
        llm_fields = self._to_field_results(llm_fields_raw)
        merged_fields = self.deps.merger.merge_fields(regex_fields, llm_fields)
        field_results = list(merged_fields.values())
        return ExtractionResult(
            document_type=filename or "unknown",
            ocr_engine=self.deps.ocr_engine.__class__.__name__ if used_ocr else None,
            ocr_confidence=ocr_confidence,
            fields=field_results,
            raw_text=raw_text,
        )

    @staticmethod
    def _to_field_results(fields: dict) -> dict[str, FieldResult]:
        results: dict[str, FieldResult] = {}
        if not fields:
            return results

        for name, field in fields.items():
            value = field.get("value") if isinstance(field, dict) else None
            if value in (None, ""):
                continue

            results[name] = FieldResult(
                name=name,
                value=value,
                confidence=float(field.get("confidence", 0.0)),
                source_quote=field.get("source_quote"),
                source="llm",
            )

        return results


def _is_text_meaningful(raw_text: str) -> bool:
    content = raw_text.strip().lower()
    if len(content) < 50:
        return False

    keywords = ("kira", "tl", "mahal")
    return any(keyword in content for keyword in keywords)


def run_extraction(file_bytes: bytes, document_type: str) -> ExtractionResult:
    text_extractor = TextExtractor(ocr_engine=TesseractOcrEngine())
    raw_text, ocr_conf, text_source = text_extractor.extract_text(file_bytes, document_type)

    if not _is_text_meaningful(raw_text):
        return ExtractionResult(
            document_type=document_type,
            ocr_engine=(
                text_extractor.ocr_engine.__class__.__name__
                if text_source == "ocr" and text_extractor.ocr_engine
                else None
            ),
            ocr_confidence=ocr_conf,
            fields=[],
            raw_text=raw_text,
        )

    regex_extractor = RegexExtractor()
    regex_fields = regex_extractor.extract_by_regex(raw_text)

    llm_client = OllamaLlmClient()
    llm_fields_raw = llm_client.extract_fields(raw_text, document_type)
    llm_fields = ExtractionPipeline._to_field_results(llm_fields_raw)

    merger = ResultMerger()
    merged_fields = merger.merge_fields(regex_fields, llm_fields)

    return ExtractionResult(
        document_type=document_type,
        ocr_engine=(
            text_extractor.ocr_engine.__class__.__name__
            if text_source == "ocr" and text_extractor.ocr_engine
            else None
        ),
        ocr_confidence=ocr_conf,
        fields=list(merged_fields.values()),
        raw_text=raw_text,
    )
