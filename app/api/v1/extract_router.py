from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile

from app.domain.models import ExtractionResult
from app.services.pipeline import run_extraction


router = APIRouter(prefix="/extract", tags=["extract"])


@router.post("/", response_model=ExtractionResult)
async def extract_contract(
    file: UploadFile = File(...),
    document_type: str = Query("kira_sozlesmesi"),
    document_type_body: str | None = Form(None),
) -> ExtractionResult:
    try:
        file_bytes = await file.read()
    except Exception as exc:  # pragma: no cover - FastAPI handles exceptions
        raise HTTPException(status_code=400, detail="Invalid file upload") from exc

    selected_document_type = document_type_body or document_type

    return run_extraction(
    file_bytes=file_bytes,
    document_type=selected_document_type,
    filename=file.filename,
)
