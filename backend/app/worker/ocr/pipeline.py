import logging
from typing import List, Optional
from .base import OCRResult
from .paddle_engine import PaddleEngine
from .easy_engine import EasyEngine

logger = logging.getLogger(__name__)

class OCRPipeline:
    def __init__(self, confidence_threshold: float = 0.9):
        self._primary_engine = None
        self._fallback_engine = None
        self.confidence_threshold = confidence_threshold

    @property
    def primary_engine(self):
        if self._primary_engine is None:
            self._primary_engine = PaddleEngine()
        return self._primary_engine

    @property
    def fallback_engine(self):
        if self._fallback_engine is None:
            self._fallback_engine = EasyEngine()
        return self._fallback_engine

    def process(self, image_path: str) -> List[OCRResult]:
        logger.info(f"Starting OCR pipeline for {image_path}")
        
        # Try primary engine
        results = self.primary_engine.extract_text(image_path)
        
        # Check average confidence
        if not results:
            avg_confidence = 0
        else:
            avg_confidence = sum(r.confidence for r in results) / len(results)

        logger.info(f"Primary engine ({self.primary_engine.get_name()}) confidence: {avg_confidence:.2f}")

        if avg_confidence < self.confidence_threshold:
            logger.info(f"Confidence below threshold ({self.confidence_threshold}). Triggering fallback.")
            fallback_results = self.fallback_engine.extract_text(image_path)
            
            # Simple merge/replace strategy: if fallback is better, use it (in real world, more complex)
            if fallback_results:
                fb_avg_confidence = sum(r.confidence for r in fallback_results) / len(fallback_results)
                logger.info(f"Fallback engine ({self.fallback_engine.get_name()}) confidence: {fb_avg_confidence:.2f}")
                
                if fb_avg_confidence > avg_confidence:
                    logger.info("Using fallback results.")
                    return fallback_results
        
        return results

# Global pipeline instance
pipeline = OCRPipeline()
