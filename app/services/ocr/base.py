from abc import ABC, abstractmethod


class OCREngine(ABC):
    @abstractmethod
    def extract_text(self, file_bytes: bytes) -> str:
        """Extract text content from an image-like input."""
        raise NotImplementedError
