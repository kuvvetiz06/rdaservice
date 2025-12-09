from dataclasses import dataclass
from typing import Optional

from app.domain.models import ExtractionResult, FieldResult
from app.services.text_extractor import TextExtractor
from app.services.ocr.base import OCREngine
from app.services.regex_extractor import RegexExtractor
from app.services.llm.base import LLMClient
from app.services.merger import ResultMerger


@dataclass
class PipelineDependencies:
    text_extractor: TextExtractor
    ocr_engine: OCREngine
    regex_extractor: RegexExtractor
    llm_client: LLMClient
    merger: ResultMerger


class ExtractionPipeline:
    def __init__(
        self,
        text_extractor: TextExtractor,
        ocr_engine: OCREngine,
        regex_extractor: RegexExtractor,
        llm_client: LLMClient,
        merger: ResultMerger,
    ) -> None:
        self.deps = PipelineDependencies(
            text_extractor=text_extractor,
            ocr_engine=ocr_engine,
            regex_extractor=regex_extractor,
            llm_client=llm_client,
            merger=merger,
        )

    def _extract_text(self, file_bytes: bytes, filename: Optional[str]) -> tuple[str, bool]:
        text = self.deps.text_extractor.extract_text(file_bytes, filename)
        if text:
            return text, False
        return self.deps.ocr_engine.extract_text(file_bytes), True

    def run(self, file_bytes: bytes, filename: Optional[str] = None) -> ExtractionResult:
        raw_text, used_ocr = self._extract_text(file_bytes, filename)
        regex_fields = self.deps.regex_extractor.extract(raw_text)
        llm_fields = self.deps.llm_client.generate_fields(raw_text, regex_fields)
        merged_fields = self.deps.merger.merge(regex_fields, llm_fields)
        field_results = [
            FieldResult(
                name=name,
                value=value,
                confidence=1.0,
                source_quote=None,
                source="merged",
            )
            for name, value in merged_fields.items()
        ]
        return ExtractionResult(
            document_type=filename or "unknown",
            ocr_engine=self.deps.ocr_engine.__class__.__name__ if used_ocr else None,
            ocr_confidence=None,
            fields=field_results,
            raw_text=raw_text,
        )
