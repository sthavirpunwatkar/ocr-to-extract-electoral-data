---
paths:
  - "backend/app/worker/ocr/**"
  - "backend/app/core/extractor.py"

# OCR Processing Rules
- Always preserve spatial layout (bounding boxes).
- docTR is the mandatory engine; do not introduce others without benchmarking.
- Extraction must handle Marathi and English scripts.
- Confidence scores below 0.7 must be flagged for review.
