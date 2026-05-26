import os
import logging
from typing import List, Any
import torch
from doctr.io import DocumentFile
from doctr.models import ocr_predictor, from_hub, crnn_vgg16_bn
from .base import OCREngine, OCRResult

logger = logging.getLogger(__name__)

class DocTREngine(OCREngine):
    def __init__(self):
        # Initialize docTR predictor
        # Use GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Initializing docTR engine on device: {self.device}")
        
        # Path for local model weights (for offline or manual integration)
        # DOCTR_CACHE_DIR is /app/.cache/doctr
        cache_dir = os.getenv("DOCTR_CACHE_DIR", "/app/.cache/doctr")
        
        # Check for multiple possible spellings of the local weights file
        local_reco_variants = [
            os.path.join(cache_dir, "models", "devanagari_reco.pt"),
            os.path.join(cache_dir, "models", "devnagari_reco.pt")
        ]
        local_reco_path = next((p for p in local_reco_variants if os.path.exists(p)), None)
        local_det_path = os.path.join(cache_dir, "models", "db_resnet50_det.pt")
        
        reco_model = None
        
        # 1. Try loading Devanagari Recognition Model from local path
        if local_reco_path:
            try:
                logger.info(f"Loading local Devanagari recognition model from {local_reco_path}...")
                
                # The model from IIT Bombay (indic-doctr) uses a specific 108-char vocabulary
                # ॲऽऐथफएऎह८॥ॉम९ुँ१ं।षघठर॓ॼड़गछिॱटऩॄऑवल५ढ़य़अञसऔयण॑क़॒ौॽशऍ॰ूीऒॊख़उज़ॻॅ३ओऌळनॠ०ेढङ४़ॢग़पऊॐज२डैभझकआदबऋखॾ॔ोइ्धतफ़ईृःा६चऱऴ७-
                local_vocab = "ॲऽऐथफएऎह८॥ॉम९ुँ१ं।षघठर॓ॼड़गछिॱटऩॄऑवल५ढ़य़अञसऔयण॑क़॒ौॽशऍ॰ूीऒॊख़उज़ॻॅ३ओऌळनॠ०ेढङ४़ॢग़पऊॐज२डैभझकआदबऋखॾ॔ोइ्धतफ़ईृःा६चऱऴ७-"
                
                # Create the architecture with the specific local vocabulary
                reco_model = crnn_vgg16_bn(pretrained=False, vocab=local_vocab)
                
                # Load weights
                checkpoint = torch.load(local_reco_path, map_location=self.device)
                # Handle both full checkpoints and state dicts
                state_dict = checkpoint if 'state_dict' not in checkpoint else checkpoint['state_dict']
                reco_model.load_state_dict(state_dict)
                logger.info("Successfully loaded local recognition model weights.")
            except Exception as e:
                logger.error(f"Failed to load local recognition model: {e}")
                reco_model = None

        # 2. Fallback to Hub if no local recognition model
        if reco_model is None:
            try:
                logger.info("Loading specialized Devanagari recognition model from Hub (mindee/doctr-torch-crnn-vgg16-bn-devanagari)...")
                # Official docTR Devanagari model
                reco_model = from_hub('mindee/doctr-torch-crnn-vgg16-bn-devanagari')
                logger.info("Successfully loaded Devanagari model from Hub.")
            except Exception as e:
                logger.warning(f"Failed to load Devanagari model from Hub: {e}. Falling back to default.")
                reco_model = 'crnn_vgg16_bn'

        # 3. Initialize Predictor
        try:
            self.model = ocr_predictor(
                det_arch='db_resnet50',
                reco_arch=reco_model,
                pretrained=True
            ).to(self.device)
            
            # 4. Optional: Override Detection Model with local weights if present
            if os.path.exists(local_det_path):
                try:
                    logger.info(f"Loading local detection model from {local_det_path}...")
                    det_checkpoint = torch.load(local_det_path, map_location=self.device)
                    det_state_dict = det_checkpoint if 'state_dict' not in det_checkpoint else det_checkpoint['state_dict']
                    self.model.det_predictor.model.load_state_dict(det_state_dict)
                    logger.info("Successfully loaded local detection model weights.")
                except Exception as e:
                    logger.error(f"Failed to load local detection model: {e}")
                    
        except Exception as e:
            logger.error(f"Critical failure initializing ocr_predictor: {e}")
            # Final fallback
            self.model = ocr_predictor(
                det_arch='db_resnet50', 
                reco_arch='crnn_vgg16_bn', 
                pretrained=True
            ).to(self.device)

    def extract_text(self, input_data: Any) -> List[OCRResult]:
        logger.info(f"docTR extracting text from input")
        
        # docTR expects list of images (numpy arrays) or paths
        # If input_data is a string path, check if it's a PDF
        if isinstance(input_data, str):
            if input_data.lower().endswith('.pdf'):
                doc = DocumentFile.from_pdf(input_data)
                # docTR can process multiple pages at once
                result = self.model(doc)
            else:
                result = self.model([input_data])
        else:
            result = self.model(input_data)
        
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
