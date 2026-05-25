import os
import json
import logging
from backend.app.worker.ocr.pipeline import pipeline

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

    for filename in files:
        file_path = os.path.join(RAW_DATA_DIR, filename)
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
            
            # Save to output directory
            output_filename = filename.replace('.pdf', '.json')
            output_path = os.path.join(EXTRACTED_DATA_DIR, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully processed {filename}. Results saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to process {filename}: {str(e)}")

if __name__ == "__main__":
    main()
