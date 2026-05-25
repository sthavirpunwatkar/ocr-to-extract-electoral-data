# OCR Backend

This is the backend for the OCR project, featuring a FastAPI API and a Celery worker.

## Architecture
- **FastAPI:** Handles file uploads and provides an interface to the system.
- **Celery:** Asynchronous task queue for document processing.
- **Redis:** Message broker for Celery.
- **MinIO:** S3-compatible object storage for uploaded PDF documents.
- **PostgreSQL:** Database for metadata and results (setup ready).
- **Elasticsearch:** Search engine for processed text (setup ready).

## Getting Started

### Prerequisites
- Docker and Docker Compose

### Running the services
1. Navigate to the project root directory.
2. Build and start the services:
   ```bash
   docker-compose up --build
   ```

### API Endpoints
- **GET /**: Health check.
- **POST /upload**: Upload a PDF file.
  - Form data: `file=@your_document.pdf`

### Storage
MinIO console is available at [http://localhost:9001](http://localhost:9001) (Credentials: `minioadmin` / `minioadmin`).
The uploaded files are stored in the `documents` bucket.

### Monitoring
You can monitor Celery tasks through the worker logs:
```bash
docker-compose logs -f worker
```
