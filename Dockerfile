FROM python:3.11-slim-bookworm

# System-level pinned dependencies (no non-deterministic libs)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libopenblas0 \
        && rm -rf /var/lib/apt/lists/*

# Environment for deterministic builds
ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "scripts/verify.py"]
