import os
import re
import logging
from typing import List, Any, Dict
import torch
import numpy as np
import cv2
from doctr.io import DocumentFile
from doctr.models import ocr_predictor, crnn_vgg16_bn
from .base import OCREngine, OCRResult

logger = logging.getLogger(__name__)

class DocTREngine(OCREngine):
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Initializing Bilingual DocTREngine on device: {self.device}")
        
        cache_dir = os.getenv("DOCTR_CACHE_DIR", "/app/.cache/doctr")
        
        # Priority order for Devanagari model weights
        marathi_reco_variants = [
            os.path.join(cache_dir, "models", "devnagari_reco_tuned.pt"),
            os.path.join(cache_dir, "models", "devnagari_reco_orig.pt"),
            os.path.join(cache_dir, "models", "devnagari_reco.pt"),
            os.path.join(cache_dir, "models", "vgg16_bn_r-d108c19c.pt")
        ]
        marathi_reco_path = next((p for p in marathi_reco_variants if os.path.exists(p)), None)
        
        # 1. Initialize Marathi Predictor
        self.marathi_model = None
        if marathi_reco_path:
            try:
                logger.info(f"Loading Marathi model from {marathi_reco_path}...")
                local_vocab = " ॲऽऐथफएऎह८॥ॉम९ुँ१ं।षघठर॓ॼड़गछिॱटऩॄऑवल५ढ़य़अञसऔयण॑क़॒ौॽशऍ॰ूीऒॊख़उज़ॻॅ३ओऌळनॠ०ेढङ४़ॢग़पऊॐज२डैभझकआदबऋखॾ॔ोइ्धतफ़ईृःा६चऱऴ७-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/.:,;()&"
                reco_model = crnn_vgg16_bn(pretrained=False, vocab=local_vocab)
                checkpoint = torch.load(marathi_reco_path, map_location=self.device, weights_only=True)
                state_dict = checkpoint if 'state_dict' not in checkpoint else checkpoint['state_dict']
                
                # Handle potential key mismatch between docTR versions
                new_state_dict = {}
                for k, v in state_dict.items():
                    nk = k.replace("features.", "feat_extractor.")
                    nk = nk.replace("classifier.", "linear.")
                    new_state_dict[nk] = v
                
                try:
                    reco_model.load_state_dict(new_state_dict)
                except:
                    # Fallback to original if transformation fails
                    reco_model.load_state_dict(state_dict)
                    
                self.marathi_model = ocr_predictor(det_arch='db_resnet50', reco_arch=reco_model, pretrained=True).to(self.device)
                logger.info("Successfully loaded Marathi predictor.")
            except Exception as e:
                logger.error(f"Failed to load Marathi model: {e}")

        # 2. Initialize English Predictor
        try:
            logger.info("Initializing English predictor (parseq)...")
            self.english_model = ocr_predictor(det_arch='db_resnet50', reco_arch='parseq', pretrained=True).to(self.device)
            logger.info("Successfully loaded English predictor.")
        except Exception as e:
            logger.warning(f"Failed to load Parseq: {e}. Falling back to default.")
            self.english_model = ocr_predictor(pretrained=True).to(self.device)

    def _deskew(self, img: np.ndarray) -> np.ndarray:
        """Correct skewness of the image."""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img
        
        coords = np.column_stack(np.where(gray < 255))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Improve visibility of faint text in electoral rolls with advanced cleaning."""
        # 1. De-skew
        img = self._deskew(img)
        
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img
            
        # 2. Advanced Denoising
        # fastNlMeansDenoising is more effective than medianBlur for scanned documents
        denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        
        # 3. Adaptive Thresholding to handle lighting variations
        # This converts to binary which can be very helpful for OCR engines
        thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        
        # 4. Sharpening (on the denoised gray image before thresholding, or on thresh?)
        # Let's sharpen the denoised image and then blend or use it
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        # 5. CLAHE for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(sharpened)
        
        # Combine: Adaptive thresholding is great for structure, CLAHE is great for details
        # We return RGB as docTR expects it
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)

    def extract_text(self, input_data: Any) -> List[OCRResult]:
        logger.info("DocTREngine extracting text (Bilingual Pass)")
        
        if isinstance(input_data, str) and input_data.lower().endswith('.pdf'):
            doc_raw = DocumentFile.from_pdf(input_data, scale=5.0)
        elif isinstance(input_data, str):
            doc_raw = DocumentFile.from_images([input_data])
        else:
            doc_raw = input_data

        preprocessed_pages = [self._preprocess_image(page) for page in doc_raw]
        
        res_marathi = []
        if self.marathi_model:
            out = self.marathi_model(preprocessed_pages)
            res_marathi = self._format_results(out.export())
            logger.info(f"Marathi results: {len(res_marathi)}")

        res_english = []
        if self.english_model:
            out = self.english_model(preprocessed_pages)
            res_english = self._format_results(out.export())
            logger.info(f"English results: {len(res_english)}")

        return self._merge_results(res_marathi, res_english)

    def _format_results(self, export: Dict) -> List[OCRResult]:
        results = []
        for page_idx, page in enumerate(export['pages']):
            for block in page['blocks']:
                for line in block['lines']:
                    for word in line['words']:
                        (xmin, ymin), (xmax, ymax) = word['geometry']
                        results.append(OCRResult(
                            text=word['value'],
                            confidence=word['confidence'],
                            box=[[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]],
                            page_num=page_idx
                        ))
        return results

    def _is_marathi(self, text: str) -> bool:
        return any('\u0900' <= c <= '\u097f' for c in text)

    def _get_overlap(self, r1: OCRResult, r2: OCRResult) -> float:
        b1 = [r1.box[0][0], r1.box[0][1], r1.box[2][0], r1.box[2][1]]
        b2 = [r2.box[0][0], r2.box[0][1], r2.box[2][0], r2.box[2][1]]
        ixmin, iymin = max(b1[0], b2[0]), max(b1[1], b2[1])
        ixmax, iymax = min(b1[2], b2[2]), min(b1[3], b2[3])
        if ixmax <= ixmin or iymax <= iymin: return 0
        inter = (ixmax - ixmin) * (iymax - iymin)
        area1 = (b1[2]-b1[0])*(b1[3]-b1[1])
        area2 = (b2[2]-b2[0])*(b2[3]-b2[1])
        
        min_area = min(area1, area2)
        if min_area <= 0: return 0
        
        return inter / min_area

    def _merge_results(self, marathi: List[OCRResult], english: List[OCRResult]) -> List[OCRResult]:
        final = []
        epic_re = re.compile(r'[A-Z]{2,4}[0-9]{6,8}|[A-Z]{3}[0-9]{7}')
        
        m_used = [False] * len(marathi)
        e_used = [False] * len(english)
        
        # 1. EPIC IDs from English (High Confidence)
        for i, e in enumerate(english):
            if epic_re.search(e.text):
                final.append(e)
                e_used[i] = True
                for j, m in enumerate(marathi):
                    if self._get_overlap(e, m) > 0.6: m_used[j] = True
        
        # 2. Devanagari from Marathi (if it's not mostly digits)
        for i, m in enumerate(marathi):
            if m_used[i]: continue
            
            # If Marathi result is mostly digits, check English pass instead
            digit_ratio = sum(c.isdigit() for c in m.text) / len(m.text) if m.text else 0
            if digit_ratio > 0.5:
                continue

            if self._is_marathi(m.text):
                final.append(m)
                m_used[i] = True
                for j, e in enumerate(english):
                    if not e_used[j] and self._get_overlap(m, e) > 0.6: e_used[j] = True
        
        # 3. Numeric/Remaining English (Strongly prefer English for digits)
        for i, e in enumerate(english):
            if e_used[i]: continue
            
            digit_ratio = sum(c.isdigit() for c in e.text) / len(e.text) if e.text else 0
            # Lower confidence threshold for digits in English
            threshold = 0.4 if digit_ratio > 0.5 else 0.6
            
            if e.confidence > threshold:
                final.append(e)
                e_used[i] = True
                for j, m in enumerate(marathi):
                    if not m_used[j] and self._get_overlap(e, m) > 0.6: m_used[j] = True
                    
        # 4. Fallback: higher confidence, but with strong bias towards English for alphanumeric
        for i, m in enumerate(marathi):
            if m_used[i]: continue
            best_e = -1
            max_o = 0
            for j, e in enumerate(english):
                if e_used[j]: continue
                o = self._get_overlap(m, e)
                if o > 0.5 and o > max_o:
                    max_o = o
                    best_e = j
            if best_e != -1:
                e_txt = english[best_e].text
                m_txt = marathi[i].text
                
                # If Marathi confidence is very low, trust English
                if marathi[i].confidence < 0.2:
                    final.append(english[best_e])
                # If English result looks like a house no or age (digits), trust it more
                elif re.search(r'\d+', e_txt) and len(e_txt) < 8:
                     final.append(english[best_e])
                elif english[best_e].confidence > m.confidence + 0.15:
                    final.append(english[best_e])
                else:
                    final.append(m)
                e_used[best_e] = True
            else:
                if m.confidence > 0.2: final.append(m)
            m_used[i] = True
            
        for i, e in enumerate(english):
            if not e_used[i] and e.confidence > 0.35:
                final.append(e)
                
        final.sort(key=lambda x: (x.page_num, x.box[0][1], x.box[0][0]))
        return final

    def get_name(self) -> str:
        return "docTR (Bilingual Ensemble v3)"
