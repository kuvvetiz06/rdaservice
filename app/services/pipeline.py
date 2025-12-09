from dataclasses import dataclass
from typing import Optional

from app.domain.models import ExtractionResult, FieldResult
from app.services.ocr.base import IOcrEngine
from app.services.regex_extractor import RegexExtractor
from app.services.llm.base import ILlmClient
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
        regex_fields = self.deps.regex_extractor.extract(raw_text)
        llm_fields = self.deps.llm_client.extract_fields(
            raw_text, filename or "kira sözleşmesi"
        )
        merged_fields = self.deps.merger.merge(regex_fields, llm_fields)
        field_results = [
            FieldResult(
                name=name,
                value=field_data.get("value"),
                confidence=float(field_data.get("confidence", 0.0)),
                source_quote=field_data.get("source_quote"),
                source=field_data.get("source", "merged"),
            )
            for name, field_data in merged_fields.items()
        ]
        return ExtractionResult(
            document_type=filename or "unknown",
            ocr_engine=self.deps.ocr_engine.__class__.__name__ if used_ocr else None,
            ocr_confidence=ocr_confidence,
            fields=field_results,
            raw_text=raw_text,
        )
