FROM python:3.10-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Use the official PyTorch CUDA index to get the correct GPU-optimized binaries
# This resolves the hash mismatch issue seen with the standard PyPI index
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --wheel-dir /app/wheels \
    -r requirements.txt \
    --index-url https://download.pytorch.org/whl/cu121 \
    --extra-index-url https://pypi.org/simple \
    --default-timeout=1000

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OCR (OpenCV, docTR, pdf2image)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install from wheels using the CUDA index for any missing dependencies
RUN pip install --no-cache-dir \
    --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

COPY . .

ENV PYTHONPATH=/app
ENV HOME=/app
ENV PYTHONUNBUFFERED=1
ENV DOCTR_CACHE_DIR=/app/.cache/doctr

# Create a non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup --home /app appuser
RUN chown -R appuser:appgroup /app
USER appuser

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
