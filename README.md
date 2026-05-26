# OCR Data Factory & Voter Management System

This project is a comprehensive system designed to extract, process, and serve electoral data (voter rolls) for mobile applications. It specializes in parsing dense PDF voter lists (e.g., Maharashtra Voter Rolls) and transforming them into structured data.

## Project Structure

- **`/backend` (Data Factory):** A Python/FastAPI application that handles the heavy lifting of OCR and data extraction.
  - **OCR Pipeline:** Uses specialized ML models (migrating to docTR) to process dense document images.
  - **Worker:** Celery-based background processing for PDF-to-Image conversion and OCR.
  - **API:** Serves job status and search functionality.
- **`/ocr-v2-staging` (Mobile Backend/Storefront):** A lightweight, read-only API built with Hono and Cloudflare Workers. It serves the processed data from Cloudflare D1 (SQLite) to mobile apps with sub-50ms latency.
- **`/mobile_app`:** The Android and iOS client applications (Flutter) that consume the electoral data.
- **`/scraper`:** Automation scripts for gathering raw PDF voter rolls.
- **`/benchmarks`:** Tools for evaluating OCR accuracy against ground-truth data.

## Architecture & Data Flow

1. **Extraction:** Raw PDFs are gathered and uploaded to MinIO storage.
2. **Processing:** The `backend` worker picks up jobs, converts PDFs to images, and runs the OCR pipeline.
3. **Structuring:** The `FieldExtractor` applies templates (YAML) to the raw OCR text to extract structured voter records (Name, ID, Age, Gender).
4. **Handoff:** Structured data is exported (typically as SQLite) and imported into the `ocr-v2` Storefront's Cloudflare D1 database.
5. **Consumption:** Mobile applications query the Storefront API for voter information.

## Tech Stack

- **Languages:** Python (Backend), TypeScript (Storefront/Mobile), Dart (Flutter).
- **Frameworks:** FastAPI, Celery, Hono (Cloudflare Workers).
- **Databases:** PostgreSQL (Backend metadata), Elasticsearch (Search), Cloudflare D1 (Storefront).
- **Storage:** MinIO (S3-compatible).
- **OCR:** docTR (Hugging Face / PyTorch).

## GPU Acceleration & Performance

The backend is optimized for **NVIDIA GPU** acceleration using CUDA 12.1. This provides a 10x-20x speedup in OCR inference, essential for processing dense voter lists.

### Requirements
- Host machine with NVIDIA GPU and drivers.
- **nvidia-container-toolkit** installed on the host.

### Setup & Run
```powershell
docker-compose up --build -d
```

## Marathi (Devanagari) OCR Support

The system uses a specialized Devanagari recognition model for Marathi voter lists.

### Manual Model Integration
To support Marathi-only documents, you must manually download the model weights:
1. Download `crnn_vgg16_bn_hindi.pt` from [IIT Bombay Indic-docTR](https://github.com/iitb-research-code/indic-doctr/releases/tag/model2).
2. Create the directory: `backend/.cache/doctr/models/`.
3. Place the file there and rename it to `devanagari_reco.pt`.
4. Restart the worker: `docker-compose restart worker`.

### Verification
Check the logs to confirm the model is loaded correctly:
```powershell
docker-compose logs -f worker
```

## Getting Started

Refer to the `README.md` in each subdirectory for specific setup and deployment instructions.
