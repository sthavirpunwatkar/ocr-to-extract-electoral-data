# Data Factory: OCR & Processing Instructions

This folder contains core instructions for agents working on the OCR Data Factory.

## Core Mandates
- **OCR Engine:** Always use **docTR** with the PyTorch backend.
- **Hardware:** Utilize GPU acceleration (CUDA) for production deployments.
- **Data Integrity:** Voter list parsing is extremely sensitive to text ordering. Ensure the OCR pipeline preserves spatial layout as much as possible.
- **Dependency Management:** Maintain a single unified framework (PyTorch) to minimize Docker image size. Avoid adding redundant OCR libraries like Paddle or EasyOCR.

## Engineering Standards
- **Docker:** All backend components must be containerized. Optimize image size by using multi-stage builds and cleaning up caches.
- **Templates:** Extraction logic is driven by YAML templates in `backend/app/templates/`. Always validate field regex against representative samples from `benchmarks/data/raw/`.

## Key Workflows
- **Migration:** When updating ML models, always perform a benchmark run using `benchmarks/scripts/evaluator.py` to ensure no regression in extraction accuracy.
- **Field Extraction:** Use `backend/app/core/extractor.py` as the primary logic for transforming OCR results into structured JSON.
