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

## Getting Started

Refer to the `README.md` in each subdirectory for specific setup and deployment instructions.
