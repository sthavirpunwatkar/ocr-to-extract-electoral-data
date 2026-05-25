from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel

class OCRResult(BaseModel):
    text: str
    confidence: float
    box: List[List[float]]  # [x, y] coordinates for 4 corners
    metadata: Dict[str, Any] = {}

class OCREngine(ABC):
    @abstractmethod
    def extract_text(self, image_path: str) -> List[OCRResult]:
        """Extract text from an image."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the engine."""
        pass
