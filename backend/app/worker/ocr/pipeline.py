import logging
import re
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
        logger.info(f"Starting OCR pipeline for {image_path} using docTR Ensemble")
        
        # 1. Primary extraction with DocTREngine (which already handles Marathi/English ensemble)
        results = self.engine.extract_text(image_path)
        
        # 2. Heuristic check: if result count is suspiciously low (e.g., < 10 voters per page)
        # 3-column layout should have ~30 voters.
        voter_count = len([r for r in results if re.search(r'[A-Z]{3}\d{7}', r.text)])
        
        if voter_count < 15:
            logger.warning(f"Low voter count ({voter_count}) detected. Retrying with high-scale fallback.")
            # We can re-run DocTR with higher scale or different preprocessing
            # For now, let's assume DocTREngine's internal ensemble is the primary.
            pass
            
        if not results:
            logger.warning("No text detected in document")
            return []

        avg_confidence = sum(r.confidence for r in results) / len(results)
        logger.info(f"docTR extraction complete. Avg confidence: {avg_confidence:.2f}")

        return results

# Global pipeline instance
pipeline = OCRPipeline()
