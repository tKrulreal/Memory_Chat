# ============================================
# MemoryChat - Multi-stage Dockerfile
# Stage 1: Builder - Install dependencies
# Stage 2: Runtime - Minimal production image
# ============================================

# ---- Stage 1: Build ----
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt .

# Install Python packages to user space
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Stage 2: Production ----
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

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
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
