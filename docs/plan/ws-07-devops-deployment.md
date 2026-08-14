# WS-07 — DevOps & Deployment

> **Mục tiêu:** Đảm bảo Backend chạy ổn định qua Docker, dễ demo, dễ scale sau này.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | WS-07 (chạy song song với tất cả) |
| Độ phức tạp | 🟢 Thấp |
| Phụ thuộc | Không có |
| Unblock | WS-08 (Test + Demo) |

---

## Trạng thái hiện tại

| Component | Status | File |
|-----------|--------|------|
| Dockerfile | ✅ Done | `Dockerfile` |
| docker-compose.yml | ✅ Done | `docker-compose.yml` |
| Makefile | ✅ Done | `Makefile` |
| .env.example | ✅ Done | `.env.example` |
| Health endpoint | ✅ Done | `/health` |
| Structured logging | ✅ Done | `src/core/logging.py` |
| Middleware | ✅ Done | `src/core/middlewares.py` |
| Backup scripts | ✅ Done | `scripts/backup.sh`, `scripts/restore.sh` |
| Seed script | ✅ Done | `scripts/seed.py` |

---

## Tech Stack Deployment

### MVP Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT STACK (MVP)                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Docker Container                      │   │
│  │                                                         │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐         │   │
│  │  │  FastAPI  │ │   LangGraph│ │   Workers  │         │   │
│  │  │  (Uvicorn)│ │   Agents   │ │  (asyncio)│         │   │
│  │  └─────┬──────┘ └────────────┘ └────────────┘         │   │
│  │        │                                               │   │
│  │  ┌─────┴─────────────────────────────────────────┐    │   │
│  │  │              Shared Volume                      │    │   │
│  │  │  ┌─────────────┐       ┌──────────────┐     │    │   │
│  │  │  │   SQLite    │       │   ChromaDB   │     │    │   │
│  │  │  │   app.db    │       │   /data      │     │    │   │
│  │  │  └─────────────┘       └──────────────┘     │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   External Services                      │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐         │   │
│  │  │  OpenAI   │ │ OpenRouter │ │  Internet  │         │   │
│  │  │   API      │ │   API      │ │            │         │   │
│  │  └────────────┘ └────────────┘ └────────────┘         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Future Stack (Post-MVP)

```
┌─────────────────────────────────────────────────────────────────┐
│                  DEPLOYMENT STACK (Future)                       │
│                                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ FastAPI │  │ FastAPI │  │ FastAPI │  │ Workers │       │
│  │   1     │  │   2     │  │   3     │  │ (Celery)│       │
│  └───┬─────┘  └───┬─────┘  └───┬─────┘  └───┬─────┘       │
│      └─────────────┼─────────────┼─────────────┘              │
│                    │             │                              │
│                    ▼             ▼                              │
│            ┌───────────────┬───────────────┐                  │
│            │    Load Balancer (Nginx)       │                  │
│            └───────────────┬───────────────┘                  │
│                            │                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │ PostgreSQL │  │   Redis    │  │   Qdrant   │           │
│  │  Primary   │  │  (Queue)  │  │  (Vector) │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## TASK-OPS-01: Dockerfile ✅

**Mô tả:** Multi-stage build Dockerfile.

**Features:**

- Python 3.11-slim base
- Non-root user (`appuser`)
- Multi-stage build (builder + runtime)
- Healthcheck directive
- Pin dependencies

**Dockerfile Structure:**

```dockerfile
# Builder stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
RUN useradd -m appuser
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages ./site-packages
COPY --from=builder /usr/local/bin ./bin
COPY . .
RUN chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## TASK-OPS-02: Docker Compose ✅

**Mô tả:** Docker Compose cho development.

**Features:**

- Single service (FastAPI + SQLite + ChromaDB)
- Persistent volumes
- Environment from .env
- Healthcheck
- Restart policy

**docker-compose.yml:**

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./.ai-log:/app/.ai-log
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## TASK-OPS-03: Makefile ✅

**Mô tả:** Development commands.

**Targets:**

```bash
# Development
make run          # Run locally
make dev          # Run with hot reload
make test         # Run tests
make test-watch   # Run tests with watch
make lint         # Lint code
make format       # Format code

# Docker
make build        # Build Docker image
make up           # Start services
make down         # Stop services
make logs         # View logs
make shell        # Shell into container

# Database
make migrate      # Run migrations
make rollback     # Rollback migration
make seed         # Seed data

# Utilities
make backup       # Backup data
make restore      # Restore data
make clean        # Clean temp files
make health       # Check health
make help         # Show help
```

---

## TASK-OPS-04: Scripts ✅

**Mô tả:** Utility scripts.

**Scripts Created:**

- `scripts/backup.sh` — Backup data directory
- `scripts/restore.sh` — Restore from backup
- `scripts/seed.py` — Seed demo data

**Seed Data:**

```python
# Demo user
demo@example.com / demo123

# 5 Contacts with profiles:
# - Nguyễn Văn A (Giáo viên)
# - Trần Thị B (Lập trình viên)
# - Lê Văn C (Bác sĩ)
# - Phạm Thị D (Kế toán)
# - Hoàng Văn E (Kiến trúc sư)

# Each contact has:
# - 10-20 messages
# - ContactMemory
# - Tags
# - Recommendations
```

---

## TASK-OPS-05: Health Check + Logging ✅

**Mô tả:** Health endpoint + structured logging.

**Health Endpoint:**

```
GET /health

Response:
{
  "status": "ok",
  "version": "2.0.0-mvp",
  "db": "ok"
}
```

**Logging:**

- JSON format (stdout)
- Request ID tracking
- AI prompt/response logging
- Log level from env

**Log Format:**

```json
{
  "event": "request",
  "request_id": "uuid",
  "method": "POST",
  "path": "/api/v1/chat",
  "status_code": 200,
  "duration_ms": 123,
  "timestamp": "2026-08-14T10:00:00Z"
}
```

---

## Deployment Commands

```bash
# 1. Build
docker build -t memorychat:latest .

# 2. Start
docker compose up -d

# 3. Check health
curl http://localhost:8000/health

# 4. Run tests
make test

# 5. Seed data
make seed

# 6. Create backup
make backup

# 7. View logs
make logs
```

---

## Kết quả mong đợi sau WS-07

```
✅ Clean clone → make run → Backend lên trong < 30s
✅ Clean clone → docker compose up → Backend lên trong < 60s
✅ Volume ./data/ chứa SQLite + ChromaDB sau khi chạy
✅ Volume persist qua lần restart
✅ make backup + make restore hoạt động
✅ Health check /health trả 200 OK + JSON body
✅ Log JSON chuẩn cho mỗi request
✅ .ai-log/ chứa JSON Lines của AI prompt + response
✅ Seed data tạo user demo + 5 Contact + messages
✅ Tài liệu trong README đầy đủ
```

---

## Trạng thái hoàn thành

| Task | Status | Evidence |
|------|--------|----------|
| TASK-OPS-01: Dockerfile | ✅ Done | `Dockerfile` |
| TASK-OPS-02: Docker Compose | ✅ Done | `docker-compose.yml` |
| TASK-OPS-03: Makefile | ✅ Done | `Makefile` |
| TASK-OPS-04: Scripts | ✅ Done | `scripts/` |
| TASK-OPS-05: Health + Logging | ✅ Done | `src/main.py`, `src/core/logging.py` |

---

## Reference

- [Deployment Architecture](../specs/architecture.md#8-deployment-architecture)

---

*Version: 2.0 (Specv2 aligned)*
*Last Updated: 2026-08-14*
