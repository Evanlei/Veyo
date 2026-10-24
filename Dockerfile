FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    VEYO_STORAGE_DIR=/app/storage VEYO_THREADS=2
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app/backend
COPY backend/requirements.txt backend/requirements-web.txt ./
# Install CPU-only wheels first; the exact model environment accepts their local version suffix.
RUN python -m pip install 'torch==2.14.0' 'torchvision==0.29.0' --index-url https://download.pytorch.org/whl/cpu \
    && python -m pip install -r requirements-web.txt
COPY backend/veyo ./veyo
COPY frontend/public/samples /app/frontend/public/samples
# Bake public pretrained weights into the image. Cold requests never download models.
RUN python -c 'from veyo.inference import DeepGazePredictor; DeepGazePredictor()' \
    && mkdir -p /app/storage \
    && groupadd --gid 10001 veyo && useradd --uid 10001 --gid veyo --no-create-home veyo \
    && chown -R veyo:veyo /app
USER veyo
EXPOSE 8080
CMD ["python", "-m", "uvicorn", "veyo.app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
