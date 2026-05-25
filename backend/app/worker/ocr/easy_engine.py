import logging
from typing import List
from .base import OCREngine, OCRResult
import easyocr

logger = logging.getLogger(__name__)

class EasyEngine(OCREngine):
    def __init__(self):
        self.name = "EasyOCR"
        try:
            # Attempt GPU initialization
            self.reader = easyocr.Reader(['en'], gpu=True)
            self.available = True
            logger.info("EasyOCR successfully initialized with GPU.")
        except Exception as e:
            logger.warning(f"GPU initialization failed for EasyOCR: {e}. Falling back to CPU.")
            try:
                self.reader = easyocr.Reader(['en'], gpu=False)
                self.available = True
            except Exception as e2:
                self.available = False
                logger.error(f"Critical failure in EasyOCR initialization: {e2}")

    def extract_text(self, image_path: str) -> List[OCRResult]:
        if not self.available:
            logger.warning("EasyOCR engine not available, skipping.")
            return []

        logger.info(f"Extracting text using {self.name} from {image_path}")
        
        try:
            # detail=1: Returns box, text, confidence
            results = self.reader.readtext(image_path, detail=1)
            
            ocr_results = []
            for (box, text, confidence) in results:
                ocr_results.append(OCRResult(
                    text=text,
                    confidence=float(confidence),
                    box=box
                ))
            return ocr_results
        except Exception as e:
            logger.error(f"OCR processing error in {self.name}: {e}")
            return []

    def get_name(self) -> str:
        return self.name
