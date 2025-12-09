from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_base_url: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field("llama3.1:8b", env="OLLAMA_MODEL")
    ocr_engine: str = Field("tesseract", env="OCR_ENGINE")
    tesseract_cmd: Optional[str] = Field(default=None, env="TESSERACT_CMD")
    tesseract_lang: str = Field("tur+eng", env="TESSERACT_LANG")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
