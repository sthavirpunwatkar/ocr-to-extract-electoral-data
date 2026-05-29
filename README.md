# Voter Tracking & OCR Campaign App

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![Flutter](https://img.shields.io/badge/Flutter-SDK-02569B?logo=flutter&logoColor=white)](https://flutter.dev/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

A professional, high-performance platform designed for political candidates and campaign teams. It transforms raw electoral data into actionable intelligence through specialized OCR pipelines, multi-lingual search, and real-time field tracking.

## 🌟 Project Mission
This application solves the critical challenge of digitizing massive, fragmented voter lists (PDF rolls) and turning them into a searchable, actionable database for ground-level election operations.

## ✨ Key Milestones & Features

### 🔍 Robust OCR Pipeline
- **Page-by-Page Processing:** Optimized for large PDF voter rolls. By processing pages individually, we have eliminated Out-of-Memory (OOM) crashes and can handle documents of arbitrary length.
- **DocTR Integration:** Utilizes Mindee/docTR with PyTorch for high-fidelity OCR on dense documents.
- **GPU Acceleration:** Optimized for **NVIDIA CUDA 12.1**, providing significant speedup in OCR inference.

### 🇮🇳 Marathi (Devanagari) Support
- **Indic-docTR Integration:** Uses specialized recognition models from IIT Bombay to ensure accurate parsing of regional language lists.
- **UTF-8 Integrity:** End-to-end fix for Marathi character encoding (mojibake), ensuring regional scripts display correctly across Backend, Web, and Mobile clients.

### 🗳️ Campaign Operations
- **Multi-lingual Fuzzy Search:** Instant search across English and Marathi scripts using **Elasticsearch**, handling common misspellings and regional variations.
- **Sentiment & Field Tracking:** Real-time logging of voter sentiment and house-to-house visit status with GPS mapping support.
- **Household Mapping:** Automatically groups voters by residence to optimize field worker routes.

## 🏗️ Architecture

- **`/backend`**: Python/FastAPI "Data Factory" handling OCR (DocTR), Celery task queues, and data structuring.
- **`/frontend`**: Next.js 15 dashboard for managers and OCR verification.
- **`/mobile_app`**: Flutter client for field workers with offline-first sync.
- **`/scraper`**: Modular suite for automated voter roll retrieval.

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python, FastAPI, Celery, Redis, PostgreSQL |
| **OCR Engine** | docTR (PyTorch), OpenCV, Indic-docTR |
| **Search** | Elasticsearch |
| **Frontend** | Next.js 15, React 19, TypeScript, TailwindCSS |
| **Mobile** | Flutter, SQLite (sqflite) |
| **Infrastructure** | Docker, Nginx, Prometheus, MinIO |

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- NVIDIA GPU + [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

### Quick Start
1. **Marathi OCR Setup**:
   - Download `crnn_vgg16_bn_hindi.pt` from [IIT Bombay Indic-docTR](https://github.com/iitb-research-code/indic-doctr/releases/tag/model2).
   - Create the directory: `backend/doctr/models/`.
   - Place the file there and rename it to `devanagari_reco.pt`.

2. **Launch the Stack**:
   ```bash
   docker-compose up --build -d
   ```

3. **Access the Services**:
   - **Frontend Dashboard**: `http://localhost:3000` (Default: `admin` / `admin123`)
   - **Backend API Docs**: `http://localhost:8000/docs`
   - **Admin Dashboard**: `http://localhost:8501` (Streamlit)
   - **MinIO Storage**: `http://localhost:9001`

## ⚖️ License
This project is licensed under the MIT License.
