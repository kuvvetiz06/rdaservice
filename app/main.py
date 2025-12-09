from fastapi import FastAPI

from app.api.v1.extract_router import router as extract_router
from app.core.logging import configure_logging


configure_logging()
app = FastAPI(title="RDA Service", version="0.1.0")
app.include_router(extract_router, prefix="/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}
