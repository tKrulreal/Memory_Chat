# ============================================
# MemoryChat - Multi-stage Dockerfile
# Stage 1: Builder - Install dependencies
# Stage 2: Runtime - Minimal production image
# ============================================

# ---- Stage 1: Build ----
# Use full image to avoid needing gcc (all packages have binary wheels)
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .

# Install Python packages with --prefix so bin/ and lib/ are structured correctly
RUN pip install --no-cache-dir --prefer-binary --prefix=/install -r requirements.txt

# ---- Stage 2: Production ----
FROM python:3.11-slim-bookworm AS runtime

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Overlay /install onto /usr/local so uvicorn, alembic etc. are on PATH for all users
COPY --from=builder /install /usr/local
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages

# Security: Create non-root user
RUN useradd -m appuser && \
    mkdir -p /app/data /app/.ai-log && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

# Healthcheck using curl (installed in runtime stage)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD curl -f http://localhost:8000/health/readiness || exit 1

# Run with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
