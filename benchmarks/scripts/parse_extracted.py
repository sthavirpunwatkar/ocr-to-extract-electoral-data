import sys
import os
import json

# Add backend to path
sys.path.append(os.path.abspath("backend"))

from app.core.templates import engine as template_engine
from app.core.extractor import extract_fields
from app.worker.ocr.base import OCRResult

EXTRACTED_DATA_DIR = "benchmarks/data/extracted"
PARSED_DATA_DIR = "benchmarks/data/parsed"

def main():
    if not os.path.exists(PARSED_DATA_DIR):
        os.makedirs(PARSED_DATA_DIR)
        
    template = template_engine.get_template("maharashtra_voter_roll")
    
    for filename in os.listdir(EXTRACTED_DATA_DIR):
        if not filename.endswith(".json"):
            continue
            
        with open(os.path.join(EXTRACTED_DATA_DIR, filename), 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        ocr_results = []
        for item in raw_data:
            ocr_results.append(OCRResult(
                text=item["text"],
                confidence=item["confidence"],
                box=item["box"]
            ))
            
        voters_data = extract_fields(ocr_results, template)
        
        parsed_records = []
        for v in voters_data:
            parsed_records.append({
                "epic": v.get("voter_id", ""),
                "name": v.get("full_name", ""),
                "relation_name": v.get("father_husband_name", ""),
                "house_no": v.get("house_number", ""),
                "age": v.get("age", ""),
                "gender": v.get("gender", "")
            })
            
        parsed_output = {
            "booth_info": {}, # Leave empty for now
            "records": parsed_records
        }
        
        with open(os.path.join(PARSED_DATA_DIR, filename), 'w', encoding='utf-8') as f:
            json.dump(parsed_output, f, indent=2, ensure_ascii=False)
            
        print(f"Parsed {filename}: extracted {len(parsed_records)} records")

if __name__ == "__main__":
    main()
