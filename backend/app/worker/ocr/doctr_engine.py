import logging
from typing import List
import torch
from doctr.models import ocr_predictor
from .base import OCREngine, OCRResult

logger = logging.getLogger(__name__)

class DocTREngine(OCREngine):
    def __init__(self):
        # Initialize docTR predictor
        # Use GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Initializing docTR engine on device: {self.device}")
        
        # We use a robust detection and recognition architecture
        self.model = ocr_predictor(
            det_arch='db_resnet50', 
            reco_arch='crnn_vgg16', 
            pretrained=True
        ).to(self.device)

    def extract_text(self, image_path: str) -> List[OCRResult]:
        logger.info(f"docTR extracting text from {image_path}")
        
        # docTR expects list of images or paths
        result = self.model([image_path])
        
        # Export result to JSON-like structure to easily parse
        export = result.export()
        
        ocr_results = []
        
        # docTR hierarchy: pages -> blocks -> lines -> words
        for page in export['pages']:
            for block in page['blocks']:
                for line in block['lines']:
                    for word in line['words']:
                        # docTR returns normalized coordinates [xmin, ymin, xmax, ymax]
                        # OCRResult expects 4 corners: [[x,y], [x,y], [x,y], [x,y]]
                        geometry = word['geometry']
                        (xmin, ymin), (xmax, ymax) = geometry
                        
                        box = [
                            [xmin, ymin],
                            [xmax, ymin],
                            [xmax, ymax],
                            [xmin, ymax]
                        ]
                        
                        ocr_results.append(OCRResult(
                            text=word['value'],
                            confidence=word['confidence'],
                            box=box
                        ))
                        
        return ocr_results

    def get_name(self) -> str:
        return "docTR (Hugging Face / PyTorch)"
