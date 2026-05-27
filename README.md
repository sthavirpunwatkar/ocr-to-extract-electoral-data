# Voter Tracking & OCR Campaign App

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![Flutter](https://img.shields.io/badge/Flutter-SDK-02569B?logo=flutter&logoColor=white)](https://flutter.dev/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

A professional, high-performance platform designed for political candidates and campaign teams. It transforms raw electoral data into actionable intelligence through specialized OCR pipelines, multi-lingual search, and real-time field tracking.

## 🌟 Project Evolution
Originally conceived as a general OCR tool for dense documents, this project has pivoted into a specialized **Election Campaign Application**. It solves the critical challenge of digitizing massive, fragmented voter lists and turning them into a searchable, actionable database for ground-level operations.

## ✨ Key Features

### 🔍 Precision OCR & Extraction
- **DocTR Integration:** Utilizes [Mindee/docTR](https://github.com/mindee/doctr) with PyTorch for high-fidelity OCR on dense PDF voter rolls.
- **Marathi (Devanagari) Support:** Specialized models from [IIT Bombay Indic-docTR](https://github.com/iitb-research-code/indic-doctr) ensure accurate parsing of regional language lists.
- **Spatial Layout Sensitivity:** Preserves the structural integrity of voter list tables during extraction.

### 🗳️ Campaign Operations
- **Multi-lingual Fuzzy Search:** Instant search across English and Marathi scripts using **Elasticsearch**, handling common misspellings and regional variations.
- **Sentiment Tracking:** Real-time logging of voter sentiment (Supportive, Neutral, Opposed) during door-to-door visits.
- **Household Mapping:** Automatically group voters by residence to optimize field worker routes.
- **Human-in-the-Loop Review:** A dedicated admin interface for side-by-side verification of OCR results with spatial highlighting.

### 📱 Performance & Scale
- **GPU Acceleration:** Optimized for **NVIDIA CUDA 12.1**, providing 10x-20x speedup in OCR inference.
- **Edge API (v2):** A lightweight storefront built with **Hono** and **Cloudflare Workers** for sub-50ms search latency on mobile devices.
- **Offline Capability:** Flutter mobile application with local SQLite storage for reliable field use in low-connectivity areas.

## 🏗️ Architecture

- **`/backend`**: Python/FastAPI "Data Factory" handling OCR, Celery task queues, and data structuring.
- **`/frontend`**: React/Vite/TypeScript dashboard for managers and OCR verification.
- **`/mobile_app`**: Flutter client for field workers.
- **`/ocr-v2-staging`**: Cloudflare Workers + D1 (SQLite) for ultra-fast voter data serving.
- **`/scraper`**: Modular suite for automating voter roll retrieval.
- **`/benchmarks`**: Accuracy evaluation framework to prevent model regressions.

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python, FastAPI, Celery, Redis, PostgreSQL |
| **OCR Engine** | docTR (PyTorch), OpenCV, Indic-docTR |
| **Search** | Elasticsearch |
| **Frontend** | React 19, Vite, TypeScript, Zustand, TanStack Query |
| **Mobile** | Flutter, SQLite (sqflite) |
| **Edge API** | Hono, Cloudflare Workers, D1 |
| **Infrastructure** | Docker, Nginx, Prometheus, MinIO |

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- NVIDIA GPU + [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) (for OCR acceleration)

### Quick Start
1. Clone the repository.
2. Build and start the infrastructure:
   ```bash
   docker-compose up --build -d
   ```
3. Access the services:
   - Backend API: `http://localhost:8000`
   - Frontend Dashboard: `http://localhost:5173`
   - Monitoring: `http://localhost:9090` (Prometheus)

## 🇮🇳 Marathi (Devanagari) Setup
For Marathi voter list support, you must manually integrate the specialized recognition model:
1. Download `crnn_vgg16_bn_hindi.pt` from [IIT Bombay Indic-docTR](https://github.com/iitb-research-code/indic-doctr/releases/tag/model2).
2. Create the directory: `backend/.cache/doctr/models/`.
3. Place the file there and rename it to `devanagari_reco.pt`.
4. Restart the worker: `docker-compose restart worker`.

## 📚 Attributions & References
We leverage several world-class open-source projects:
- **[Mindee/docTR](https://github.com/mindee/doctr)** - The core engine for our OCR pipeline.
- **[IIT Bombay Indic-docTR](https://github.com/iitb-research-code/indic-doctr)** - Specialized Devanagari models.
- **[FastAPI](https://fastapi.tiangolo.com/)** - High-performance Python API framework.
- **[Flutter](https://flutter.dev/)** - Multi-platform mobile development.

## ⚖️ License
This project is licensed under the MIT License - see the LICENSE file for details.

---
*Empowering campaigns with data-driven precision.*
