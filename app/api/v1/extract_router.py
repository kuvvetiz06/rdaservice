from fastapi import APIRouter, File, UploadFile, HTTPException

from app.domain.models import ExtractionResponse
from app.services.pipeline import ExtractionPipeline
from app.services.regex_extractor import RegexExtractor
from app.services.text_extractor import TextExtractor
from app.services.ocr.tesseract_engine import TesseractEngine
from app.services.llm.ollama_client import OllamaClient
from app.services.merger import ResultMerger


router = APIRouter(prefix="/extract", tags=["extract"])


@router.post("/", response_model=ExtractionResponse)
async def extract_contract(file: UploadFile = File(...)) -> ExtractionResponse:
    try:
        file_bytes = await file.read()
    except Exception as exc:  # pragma: no cover - FastAPI handles exceptions
        raise HTTPException(status_code=400, detail="Invalid file upload") from exc

    pipeline = ExtractionPipeline(
        text_extractor=TextExtractor(),
        ocr_engine=TesseractEngine(),
        regex_extractor=RegexExtractor(),
        llm_client=OllamaClient(),
        merger=ResultMerger(),
    )

    result = pipeline.run(file_bytes=file_bytes, filename=file.filename)
    return ExtractionResponse(raw_text=result.raw_text, fields=result.fields)
