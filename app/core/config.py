from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    ollama_model: str = Field("llama3.1:8b", env="OLLAMA_MODEL")
    tesseract_lang: str = Field("eng", env="TESSERACT_LANG")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
