from abc import ABC, abstractmethod
from typing import Dict, Optional


class LLMClient(ABC):
    @abstractmethod
    def generate_fields(
        self, raw_text: str, existing_fields: Dict[str, Optional[str]]
    ) -> Dict[str, Optional[str]]:
        """Generate structured data from text."""
        raise NotImplementedError
