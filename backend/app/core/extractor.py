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

    def segment_records(self, ocr_results: List[OCRResult]) -> List[List[OCRResult]]:
        records = []
        # Filter out header/footer (y < 0.08 or y > 0.95 roughly)
        body_results = [r for r in ocr_results if 0.08 < r.box[0][1] < 0.95]
        
        # Group into 3 columns based on x_center
        cols = {0: [], 1: [], 2: []}
        for r in body_results:
            x_center = (r.box[0][0] + r.box[1][0]) / 2.0
            if x_center < 0.33:
                cols[0].append(r)
            elif x_center < 0.66:
                cols[1].append(r)
            else:
                cols[2].append(r)
                
        # For each column, group by y_center into rows
        for col_idx in range(3):
            col_results = cols[col_idx]
            if not col_results:
                continue
                
            # Sort by y_center
            col_results.sort(key=lambda r: (r.box[0][1] + r.box[3][1]) / 2.0)
            
            current_record = []
            for r in col_results:
                y_center = (r.box[0][1] + r.box[3][1]) / 2.0
                if not current_record:
                    current_record.append(r)
                else:
                    prev_r = current_record[-1]
                    prev_y_center = (prev_r.box[0][1] + prev_r.box[3][1]) / 2.0
                    # If gap > threshold (e.g., 0.045 of page height), start new record
                    if y_center - prev_y_center > 0.045:
                        records.append(current_record)
                        current_record = [r]
                    else:
                        current_record.append(r)
            if current_record:
                records.append(current_record)
                
        return records

    def extract_record(self, record_results: List[OCRResult]) -> Dict[str, Any]:
        extracted_data = {}
        
        cleaned_results = []
        for res in record_results:
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
                            logger.debug(f"Found {field_name} via regex: {extracted_data[field_name]}")

        # 2. Second pass: Label-based matching (Fuzzy-ish)
        for field_name, field_config in self.template.fields.items():
            if field_name in extracted_data:
                continue
                
            if field_config.label:
                labels = field_config.label.split('|')
                for label in labels:
                    label_pattern = re.compile(re.escape(label), re.IGNORECASE)
                    
                    for i, text in enumerate(cleaned_results):
                        match = label_pattern.search(text)
                        if match:
                            val = text[match.end():].strip().lstrip(':').strip()
                            if val and len(val) > 1:
                                extracted_data[field_name] = val
                                logger.debug(f"Found {field_name} via label '{label}': {val}")
                                break
                            elif i + 1 < len(cleaned_results):
                                val = cleaned_results[i+1]
                                if val and len(val) > 1:
                                    extracted_data[field_name] = val
                                    logger.debug(f"Found {field_name} via label '{label}' (next block): {val}")
                                    break
                    if field_name in extracted_data:
                        break

        # 3. Third pass: Option-based matching (for gender)
        for field_name, field_config in self.template.fields.items():
            if field_name in extracted_data:
                continue
                
            if field_config.options:
                for text in cleaned_results:
                    for option in field_config.options:
                        if option.lower() in text.lower():
                            extracted_data[field_name] = option
                            break
                    if field_name in extracted_data:
                        break

        return extracted_data

    def extract(self, ocr_results: List[OCRResult]) -> List[Dict[str, Any]]:
        records = self.segment_records(ocr_results)
        logger.info(f"Segmented page into {len(records)} records based on 3-column grid layout.")
        
        all_extracted_data = []
        for record_results in records:
            data = self.extract_record(record_results)
            # Add raw_ocr_data specific to this segmented record
            data["_raw_ocr_data"] = [r.dict() for r in record_results]
            
            # To avoid saving empty/junk records, ensure we have at least one valid field extracted
            if any(k != "_raw_ocr_data" for k in data.keys()):
                all_extracted_data.append(data)
                
        return all_extracted_data

def extract_fields(ocr_results: List[OCRResult], template: TemplateConfig) -> List[Dict[str, Any]]:
    extractor = FieldExtractor(template)
    return extractor.extract(ocr_results)
