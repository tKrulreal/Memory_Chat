# ============================================
# MemoryChat - Production Dockerfile
# Auto-runs migrations on startup
# ============================================

# ---- Stage 1: Build ----
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .

# Install Python packages with --prefix so bin/ and lib/ are structured correctly
RUN pip install --no-cache-dir --prefer-binary --prefix=/install -r requirements.txt

# ---- Stage 2: Production ----
FROM python:3.11-slim-bookworm AS runtime

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Overlay /install onto /usr/local so uvicorn, alembic etc. are on PATH for all users
COPY --from=builder /install /usr/local
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/.ai-log && chmod 777 /app/.ai-log

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/readiness')" || exit 1

# Auto-run migrations and start uvicorn
# NOTE: docker-compose waits for postgres to be healthy before starting backend
CMD ["sh", "-c", "echo 'Running database migrations...' && python -m alembic upgrade head && echo 'Starting uvicorn...' && exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 1"]
