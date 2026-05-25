import re
import logging
from typing import List, Dict, Any, Optional
from app.worker.ocr.base import OCRResult
from app.core.templates import TemplateConfig

logger = logging.getLogger(__name__)

class FieldExtractor:
    def __init__(self, template: TemplateConfig):
        self.template = template
        self.marathi_to_english = {
            '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
            '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
        }

    def _clean_text(self, text: str) -> str:
        # Convert Marathi digits to English
        for m, e in self.marathi_to_english.items():
            text = text.replace(m, e)
        return text.strip()

    def extract(self, ocr_results: List[OCRResult]) -> Dict[str, Any]:
        extracted_data = {}
        
        # Pre-clean all OCR texts and keep mapping to original index
        cleaned_results = []
        for res in ocr_results:
            cleaned_text = self._clean_text(res.text)
            cleaned_results.append(cleaned_text)

        # 1. First pass: Regex matching (strongest signal)
        for field_name, field_config in self.template.fields.items():
            if field_config.regex:
                pattern = re.compile(field_config.regex)
                for text in cleaned_results:
                    match = pattern.search(text)
                    if match:
                        if field_name not in extracted_data:
                            extracted_data[field_name] = match.group(0)
                            logger.info(f"Found {field_name} via regex: {extracted_data[field_name]}")

        # 2. Second pass: Label-based matching (Fuzzy-ish)
        for field_name, field_config in self.template.fields.items():
            if field_name in extracted_data:
                continue
                
            if field_config.label:
                labels = field_config.label.split('|')
                for label in labels:
                    # Match label case-insensitively and allowing for some whitespace
                    label_pattern = re.compile(re.escape(label), re.IGNORECASE)
                    
                    for i, text in enumerate(cleaned_results):
                        match = label_pattern.search(text)
                        if match:
                            # Value might be in the same block after a colon or space
                            val = text[match.end():].strip().lstrip(':').strip()
                            if val and len(val) > 1: # Avoid single chars
                                extracted_data[field_name] = val
                                logger.info(f"Found {field_name} via label '{label}': {val}")
                                break
                            # Or it might be in the next block
                            elif i + 1 < len(cleaned_results):
                                val = cleaned_results[i+1]
                                if val and len(val) > 1:
                                    extracted_data[field_name] = val
                                    logger.info(f"Found {field_name} via label '{label}' (next block): {val}")
                                    break
                    if field_name in extracted_data:
                        break

        # 3. Third pass: Option-based matching (for gender)
        for field_name, field_config in self.template.fields.items():
            if field_name in extracted_data:
                continue
                
            if field_config.options:
                for res in ocr_results:
                    for option in field_config.options:
                        if option.lower() in res.text.lower():
                            extracted_data[field_name] = option
                            break
                    if field_name in extracted_data:
                        break

        return extracted_data

def extract_fields(ocr_results: List[OCRResult], template: TemplateConfig) -> Dict[str, Any]:
    extractor = FieldExtractor(template)
    return extractor.extract(ocr_results)
