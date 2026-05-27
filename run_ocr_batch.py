import os
import json
import logging
import sys

# Ensure backend is in path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Set default cache dir for doctr if not set
if not os.getenv("DOCTR_CACHE_DIR"):
    os.environ["DOCTR_CACHE_DIR"] = os.path.join(os.getcwd(), 'backend', '.cache', 'doctr')

from app.worker.ocr.pipeline import pipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

RAW_DATA_DIR = "benchmarks/data/raw"
EXTRACTED_DATA_DIR = "benchmarks/data/extracted"

def main():
    if not os.path.exists(EXTRACTED_DATA_DIR):
        os.makedirs(EXTRACTED_DATA_DIR)

    files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith('.pdf')]
    logger.info(f"Found {len(files)} files to process in {RAW_DATA_DIR}")

    stats = {"success": 0, "failed": 0, "skipped": 0}

    for filename in files:
        file_path = os.path.join(RAW_DATA_DIR, filename)
        output_filename = filename.replace('.pdf', '.json')
        output_path = os.path.join(EXTRACTED_DATA_DIR, output_filename)

        if os.path.exists(output_path):
            logger.info(f"Skipping {filename} (already processed)")
            stats["skipped"] += 1
            continue

        logger.info(f"Processing {filename}...")
        
        try:
            # Run the ensemble pipeline
            results = pipeline.process(file_path)
            
            # Format results as JSON
            extracted_data = [
                {
                    "text": r.text,
                    "confidence": r.confidence,
                    "box": r.box
                }
                for r in results
            ]
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully processed {filename}. Results saved to {output_path}")
            stats["success"] += 1
            
        except Exception as e:
            logger.error(f"Failed to process {filename}: {str(e)}")
            stats["failed"] += 1

    logger.info(f"Batch processing complete. Summary: {json.dumps(stats)}")

if __name__ == "__main__":
    main()
