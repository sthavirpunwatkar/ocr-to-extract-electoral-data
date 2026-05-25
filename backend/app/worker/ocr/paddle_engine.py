import logging
from typing import List
from .base import OCREngine, OCRResult
from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)

class PaddleEngine(OCREngine):
    def __init__(self):
        self.name = "PaddleOCR"
        try:
            # Attempt GPU initialization
            self.ocr = PaddleOCR(use_angle_cls=True, lang='mr', use_gpu=True)
            self.available = True
            logger.info("PaddleOCR successfully initialized with GPU for Marathi.")
        except Exception as e:
            logger.warning(f"GPU initialization failed for PaddleOCR: {e}. Falling back to CPU.")
            try:
                self.ocr = PaddleOCR(use_angle_cls=True, lang='mr', use_gpu=False)
                self.available = True
            except Exception as e2:
                self.available = False
                logger.error(f"Critical failure in PaddleOCR initialization: {e2}")

    def extract_text(self, image_path: str) -> List[OCRResult]:
        if not self.available:
            logger.warning("PaddleOCR engine not available, skipping.")
            return []

        logger.info(f"Extracting text using {self.name} from {image_path}")
        
        try:
            results = self.ocr.ocr(image_path, cls=True)
            
            ocr_results = []
            if results and results[0]:
                for line in results[0]:
                    box = line[0]
                    text, confidence = line[1]
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
