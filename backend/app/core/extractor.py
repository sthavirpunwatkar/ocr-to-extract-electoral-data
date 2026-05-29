import re
import logging
from typing import List, Dict, Any, Optional
from app.worker.ocr.base import OCRResult
from app.core.templates import TemplateConfig

logger = logging.getLogger(__name__)

from Levenshtein import distance as lev_dist

class FieldExtractor:
    def __init__(self, template: TemplateConfig):
        self.template = template
        self.marathi_to_english = {
            '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
            '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
        }
        # Common Marathi Surnames for correction
        self.common_surnames = [
            "पाटील", "देशमुख", "कदम", "पवार", "चव्हाण", "कुलकर्णी", "जोशी", "गायकवाड",
            "शिंदे", "कुलकर्णी", "मोरे", "साळुंखे", "जाधव", "भोसले", "थोरात", "माने",
            "वाघमारे", "कांबळे", "गांधी", "शहा", "मेहता", "देशपांडे", "घाडगे", "सावंत"
        ]

    def _correct_marathi_surname(self, text: str) -> str:
        """Correct common Marathi surnames using Levenshtein distance."""
        words = text.split()
        if not words:
            return text
        
        last_word = words[-1]
        best_match = last_word
        min_dist = 2 # Max distance of 1-2 chars
        
        for surname in self.common_surnames:
            d = lev_dist(last_word, surname)
            if d < min_dist:
                min_dist = d
                best_match = surname
        
        if best_match != last_word:
            words[-1] = best_match
            return " ".join(words)
        return text

    def _validate_epic_id(self, epic_id: str) -> bool:
        """Validate EPIC ID format (3 letters + 7 digits)."""
        if not epic_id:
            return False
        # Basic regex check
        if re.match(r'^[A-Z]{3}\d{7}$', epic_id):
            return True
        # Old format check
        if '/' in epic_id:
            return True
        return False

    def _clean_text(self, text: str) -> str:
        # Convert Marathi digits to English
        for m, e in self.marathi_to_english.items():
            text = text.replace(m, e)
        # Basic character cleaning - remove common noise characters but keep Marathi
        text = re.sub(r'[|\[\]{}()<>~`!@#$%^&*_=+\\]', '', text)
        return text.strip()

    def segment_records(self, ocr_results: List[OCRResult]) -> List[List[OCRResult]]:
        records = []
        # Disable header filter for debugging
        body_results = [r for r in ocr_results if 0.01 < (r.box[0][1] + r.box[1][1])/2.0 < 0.99]
        
        if not body_results:
            return []

        # EPIC Regex for Maharashtra
        epic_pattern = re.compile(r'[A-Z]{3}\d{7}|\d{10}')

        # Dynamic Column Detection
        x_centers = [(r.box[0][0] + r.box[1][0]) / 2.0 for r in body_results]
        clusters = {}
        for x in x_centers:
            bucket = round(x, 1)
            clusters[bucket] = clusters.get(bucket, 0) + 1
        
        sorted_clusters = sorted(clusters.items(), key=lambda x: x[1], reverse=True)[:3]
        cluster_centers = sorted([c[0] for c in sorted_clusters])
        
        if not cluster_centers:
             cluster_centers = [0.16, 0.50, 0.83]

        cols = {i: [] for i in range(len(cluster_centers))}
        for r in body_results:
            x_center = (r.box[0][0] + r.box[1][0]) / 2.0
            best_col = 0
            min_dist = 1.0
            for i, center in enumerate(cluster_centers):
                dist = abs(x_center - center)
                if dist < min_dist:
                    min_dist = dist
                    best_col = i
            
            if min_dist < 0.18: # Looser column assignment
                cols[best_col].append(r)
                
        for col_idx in range(len(cluster_centers)):
            col_results = cols[col_idx]
            if not col_results:
                continue
                
            col_results.sort(key=lambda r: r.box[0][1])
            
            current_record = []
            
            for i, r in enumerate(col_results):
                text = self._clean_text(r.text)
                is_epic = epic_pattern.search(text)
                
                if current_record:
                    y_dist_from_prev = r.box[0][1] - current_record[-1].box[1][1]
                    y_dist_from_start = r.box[0][1] - current_record[0].box[0][1]
                    
                    split_needed = False
                    
                    # Looser split heuristics
                    if is_epic and y_dist_from_start > 0.06: # Increased from 0.03
                        split_needed = True
                    elif y_dist_from_prev > 0.06: # Increased from 0.045
                        split_needed = True
                    elif y_dist_from_start > 0.13: # Increased from 0.11
                        split_needed = True
                        
                    if split_needed:
                        records.append(current_record)
                        current_record = [r]
                        continue
                
                current_record.append(r)
            
            if current_record:
                records.append(current_record)
                
        return records

    def extract_record(self, record_results: List[OCRResult]) -> Dict[str, Any]:
        extracted_data = {}
        used_indices = set()
        
        # Sort results within record: Y first, then X
        record_results.sort(key=lambda r: (r.box[0][1], r.box[0][0]))
        
        cleaned_texts = [self._clean_text(res.text) for res in record_results]

        # 1. Voter ID (EPIC) - Must match Maharashtra pattern
        for i, text in enumerate(cleaned_texts):
            # Clean text specifically for EPIC (remove spaces, etc.)
            epic_candidate = re.sub(r'[^A-Z0-9]', '', text)
            if re.search(r'[A-Z]{3}\d{7}', epic_candidate):
                val = re.search(r'[A-Z]{3}\d{7}', epic_candidate).group(0)
                if self._validate_epic_id(val):
                    extracted_data["voter_id"] = val
                    used_indices.add(i)
                    break

        # 2. Label-based matching (Multi-pass)
        flex_patterns = {
            "full_name": r"ना[वधम]|^[वा]व$|Name",
            "father_name": r"व[डीी][लळ]|Father",
            "husband_name": r"प[तीी]|Husband",
            "mother_name": r"[आअ][ईी]|Mother",
            "age": r"व[यय़]|Age",
            "gender": r"लि[ंगगं]|Gender",
            "house_no": r"घ[रऱ]|House"
        }
        
        # Pass 2a: Value in SAME block as label
        for field_name, pattern in flex_patterns.items():
            if field_name in extracted_data: continue
            label_re = re.compile(pattern + r"[:\s\-\.]*", re.IGNORECASE)
            for i, text in enumerate(cleaned_texts):
                if i in used_indices: continue
                match = label_re.search(text)
                if match:
                    val = text[match.end():].strip()
                    if val and len(val) >= 1:
                        # Clean value from next labels
                        for _, p2 in flex_patterns.items():
                            if re.search(p2, val, re.IGNORECASE):
                                val = re.split(p2, val, flags=re.IGNORECASE)[0].strip()
                                break
                        if val:
                            extracted_data[field_name] = val
                            used_indices.add(i)
                            break
                            
        # Pass 2b: Value in NEXT block
        for field_name, pattern in flex_patterns.items():
            if field_name in extracted_data: continue
            label_re = re.compile(pattern + r"[:\s\-\.]*$", re.IGNORECASE)
            for i, text in enumerate(cleaned_texts):
                if i in used_indices: continue
                if label_re.search(text):
                    # Look ahead 1-2 blocks
                    for j in range(i+1, min(i+3, len(cleaned_texts))):
                        if j in used_indices: continue
                        val = cleaned_texts[j]
                        if len(val) >= 1:
                            extracted_data[field_name] = val
                            used_indices.add(i)
                            used_indices.add(j)
                            break
                    if field_name in extracted_data: break

        # 3. Positional & Type-based Heuristics (Age, House No, Gender)
        # Age is usually 2 digits near 'वय' or at the end
        if "age" not in extracted_data:
            # Look for 2-3 digits in blocks that don't look like EPIC or Name
            for i in range(len(cleaned_texts)-1, -1, -1):
                if i in used_indices: continue
                text = cleaned_texts[i]
                match = re.search(r"\b(\d{2,3})\b", text)
                if match:
                    val = match.group(1)
                    if 18 <= int(val) <= 110:
                        extracted_data["age"] = val
                        used_indices.add(i)
                        break

        # House No is usually after 'घर' or a alphanumeric code
        if "house_no" not in extracted_data:
            for i, text in enumerate(cleaned_texts):
                if i in used_indices: continue
                # Stricter house no: either follows 'घर' or is at least 2 chars if it's just digits
                if "घर" in record_results[i].text or "House" in record_results[i].text:
                     match = re.search(r"(\d+[\/\-]?\w*)", text)
                     if match:
                         extracted_data["house_no"] = match.group(1)
                         used_indices.add(i)
                         break
                # Fallback to any alphanumeric block that's not name/epic
                elif re.match(r"^\d+[\/\-]?\w*$", text) and len(text) >= 2:
                     extracted_data["house_no"] = text
                     used_indices.add(i)
                     break

        # Gender: स्त्री/पुरुष or F/M
        if "gender" not in extracted_data:
            for i, text in enumerate(cleaned_texts):
                if i in used_indices: continue
                if any(k in text for k in ["स्त्री", "पुरुष", "Female", "Male"]):
                    extracted_data["gender"] = "स्त्री" if ("स्त्री" in text or "Female" in text) else "पुरुष"
                    used_indices.add(i)
                    break

        # 4. Name Fallback (The remaining most likely block)
        if "full_name" not in extracted_data:
            for i, text in enumerate(cleaned_texts):
                if i in used_indices: continue
                if len(text) > 5 and not text.isdigit() and not self._is_marathi_label(text):
                    extracted_data["full_name"] = text
                    used_indices.add(i)
                    break

        # 5. Generic Regex Fallback
        for field_name, field_config in self.template.fields.items():
            if field_name in extracted_data:
                continue
            
            if field_config.regex:
                pattern = re.compile(field_config.regex)
                for i, text in enumerate(cleaned_texts):
                    if i in used_indices: continue
                    match = pattern.search(text)
                    if match:
                        extracted_data[field_name] = match.group(0)
                        used_indices.add(i)
                        break

        # 6. Post-process names
        if "full_name" in extracted_data:
            extracted_data["full_name"] = self._correct_marathi_surname(extracted_data["full_name"])
        if "father_name" in extracted_data:
            extracted_data["father_name"] = self._correct_marathi_surname(extracted_data["father_name"])
        if "husband_name" in extracted_data:
            extracted_data["husband_name"] = self._correct_marathi_surname(extracted_data["husband_name"])

        return extracted_data

    def _is_marathi_label(self, text: str) -> bool:
        labels = ["नाव", "वडिलांचे", "पतीचे", "वय", "लिंग", "घर", "क्रमांक"]
        return any(l in text for l in labels)

    def extract(self, ocr_results: List[OCRResult]) -> List[Dict[str, Any]]:
        # Group results by page
        pages = {}
        for r in ocr_results:
            if r.page_num not in pages:
                pages[r.page_num] = []
            pages[r.page_num].append(r)
            
        all_extracted_data = []
        for page_num in sorted(pages.keys()):
            page_results = pages[page_num]
            records = self.segment_records(page_results)
            logger.info(f"Page {page_num}: Segmented into {len(records)} records.")
            
            for record_results in records:
                data = self.extract_record(record_results)
                data["page_num"] = page_num
                
                # Minimum quality check
                field_keys = [k for k in data.keys() if k not in ["_raw_ocr_data", "page_num"]]
                
                if not field_keys:
                    continue
                
                # Add raw_ocr_data
                data["_raw_ocr_data"] = [r.dict() for r in record_results]
                all_extracted_data.append(data)
                
        return all_extracted_data

def extract_fields(ocr_results: List[OCRResult], template: TemplateConfig) -> List[Dict[str, Any]]:
    extractor = FieldExtractor(template)
    return extractor.extract(ocr_results)
