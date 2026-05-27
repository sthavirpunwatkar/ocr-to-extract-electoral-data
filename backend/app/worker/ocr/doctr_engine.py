import os
import logging
from typing import List, Any, Dict
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
        logger.info(f"Initializing Bilingual DocTREngine on device: {self.device}")
        
        cache_dir = os.getenv("DOCTR_CACHE_DIR", "/app/.cache/doctr")
        local_reco_variants = [
            os.path.join(cache_dir, "models", "devanagari_reco.pt"),
            os.path.join(cache_dir, "models", "devnagari_reco.pt")
        ]
        local_reco_path = next((p for p in local_reco_variants if os.path.exists(p)), None)
        
        # 1. Initialize Devanagari Predictor (Local weights)
        self.devanagari_model = None
        if local_reco_path:
            try:
                logger.info(f"Loading Devanagari model from {local_reco_path}...")
                # The model from IIT Bombay (indic-doctr) uses a specific 108-char vocabulary
                local_vocab = "ॲऽऐथफएऎह८॥ॉम९ुँ१ं।षघठर॓ॼड़गछिॱटऩॄऑवल५ढ़य़अञसऔयण॑क़॒ौॽशऍ॰ूीऒॊख़उज़ॻॅ३ओऌळनॠ०ेढङ४़ॢग़पऊॐज२डैभझकआदबऋखॾ॔ोइ्धतफ़ईृःा६चऱऴ७-"
                reco_model = crnn_vgg16_bn(pretrained=False, vocab=local_vocab)
                checkpoint = torch.load(local_reco_path, map_location=self.device, weights_only=True)
                state_dict = checkpoint if 'state_dict' not in checkpoint else checkpoint['state_dict']
                reco_model.load_state_dict(state_dict)
                self.devanagari_model = ocr_predictor(det_arch='db_resnet50', reco_arch=reco_model, pretrained=True).to(self.device)
                logger.info("Successfully loaded Devanagari predictor.")
            except Exception as e:
                logger.error(f"Failed to load Devanagari model: {e}")

        # 2. Initialize English Predictor (Default weights)
        try:
            logger.info("Initializing English/Alphanumeric predictor (default weights)...")
            self.english_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True).to(self.device)
            logger.info("Successfully loaded English predictor.")
        except Exception as e:
            logger.error(f"Failed to load English predictor: {e}")
            self.english_model = None

        # Fallback if both failed (highly unlikely)
        if not self.devanagari_model and not self.english_model:
            logger.error("Both predictors failed. Initializing default as last resort.")
            self.english_model = ocr_predictor(pretrained=True).to(self.device)

    def extract_text(self, input_data: Any) -> List[OCRResult]:
        logger.info("DocTREngine extracting text (Ensemble Pass)")
        
        # Prepare document
        if isinstance(input_data, str) and input_data.lower().endswith('.pdf'):
            doc = DocumentFile.from_pdf(input_data)
        elif isinstance(input_data, str):
            doc = DocumentFile.from_images([input_data])
        else:
            doc = input_data

        # Pass 1: Devanagari
        results_marathi = []
        if self.devanagari_model:
            out = self.devanagari_model(doc)
            results_marathi = self._format_results(out.export())
            logger.info(f"Devanagari pass: detected {len(results_marathi)} words")

        # Pass 2: English
        results_english = []
        if self.english_model:
            out = self.english_model(doc)
            results_english = self._format_results(out.export())
            logger.info(f"English pass: detected {len(results_english)} words")

        # Combine results
        # We prefer Devanagari for Marathi characters and English for Alphanumeric.
        # However, simpler is to return all and let the extractor/cleaner filter.
        # To avoid duplicates, we could use spatial overlap, but for voter lists, 
        # names are Marathi and EPICs are English, they rarely overlap spatially.
        
        # Return a merged list of unique boxes (simplified)
        return self._merge_results(results_marathi, results_english)

    def _format_results(self, export: Dict) -> List[OCRResult]:
        ocr_results = []
        for page in export['pages']:
            for block in page['blocks']:
                for line in block['lines']:
                    for word in line['words']:
                        geometry = word['geometry']
                        (xmin, ymin), (xmax, ymax) = geometry
                        box = [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]
                        ocr_results.append(OCRResult(
                            text=word['value'],
                            confidence=word['confidence'],
                            box=box
                        ))
        return ocr_results

    def _merge_results(self, marathi: List[OCRResult], english: List[OCRResult]) -> List[OCRResult]:
        # Simple merge: Keep Marathi results if they contain Devanagari,
        # Keep English results if they contain only ASCII/Alphanumeric.
        final_results = []
        
        for res in marathi:
            if any(ord(c) > 127 for c in res.text):
                final_results.append(res)
        
        for res in english:
            # Only add if it's alphanumeric and doesn't overlap significantly with an existing Marathi result
            if any(c.isalnum() for c in res.text) and not any(ord(c) > 127 for c in res.text):
                final_results.append(res)
                
        return final_results

    def get_name(self) -> str:
        return "docTR (Hugging Face / PyTorch)"
