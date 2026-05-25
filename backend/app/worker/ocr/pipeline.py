import logging
from typing import List, Optional
from .base import OCRResult
from .doctr_engine import DocTREngine

logger = logging.getLogger(__name__)

class OCRPipeline:
    def __init__(self, confidence_threshold: float = 0.7):
        self._engine = None
        self.confidence_threshold = confidence_threshold

    @property
    def engine(self):
        if self._engine is None:
            self._engine = DocTREngine()
        return self._engine

    def process(self, image_path: str) -> List[OCRResult]:
        logger.info(f"Starting OCR pipeline for {image_path} using docTR")
        
        results = self.engine.extract_text(image_path)
        
        if not results:
            logger.warning("No text detected in document")
            return []

        avg_confidence = sum(r.confidence for r in results) / len(results)
        logger.info(f"docTR extraction complete. Avg confidence: {avg_confidence:.2f}")

        return results

# Global pipeline instance
pipeline = OCRPipeline()
