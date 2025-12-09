from dataclasses import dataclass
from typing import Optional

from app.domain.models import ExtractionResult
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

    def _extract_text(self, file_bytes: bytes, filename: Optional[str]) -> str:
        text = self.deps.text_extractor.extract_text(file_bytes, filename)
        if text:
            return text
        return self.deps.ocr_engine.extract_text(file_bytes)

    def run(self, file_bytes: bytes, filename: Optional[str] = None) -> ExtractionResult:
        raw_text = self._extract_text(file_bytes, filename)
        regex_fields = self.deps.regex_extractor.extract(raw_text)
        llm_fields = self.deps.llm_client.generate_fields(raw_text, regex_fields)
        merged_fields = self.deps.merger.merge(regex_fields, llm_fields)
        return ExtractionResult(raw_text=raw_text, fields=merged_fields)
