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

> **Specification Reference:**
> - [Deployment - MVP Deployment](../specs/deployment.md#2-mvp-deployment)
> - [Deployment - Phase 2 Deployment](../specs/deployment.md#3-phase-2-deployment-docker-compose)
> - [Deployment - Environment Configuration](../specs/deployment.md#5-environment-configuration)

---

## Trạng thái hiện tại

- ✅ `Dockerfile` - Multi-stage build với non-root user, healthcheck
- ✅ `docker-compose.yml` - Volumes, healthcheck, restart policy
- ✅ `Makefile` - Đầy đủ targets (run, test, backup, restore, logs, shell, etc.)
- ✅ `.env.example` - Đã cập nhật với config mới
- ✅ Health check endpoint - `/health` trả về status, version, db
- ✅ Structured logging - JSON output với structlog
- ✅ Backup/restore scripts - `scripts/backup.sh`, `scripts/restore.sh`
- ✅ Seed script - `scripts/seed.py` với demo user + 5 contacts

---

## TASK-OPS-01: Dockerfile review + multi-stage ✅

**Mục tiêu:** Hoàn thiện Dockerfile — multi-stage build, non-root user, pinned version.

**Checklist:**
- [x] Review Dockerfile hiện tại
- [x] Multi-stage build (builder stage + runtime stage)
- [x] Non-root user trong container (`appuser`)
- [x] Pin Python version 3.11-slim
- [x] Cài `requirements.txt` từ freeze
- [x] `HEALTHCHECK` directive (gọi `/health` mỗi 30s)
- [x] Copy source code sau khi install deps (tận dụng cache)
- [x] Giảm image size (clean apt, no cache)

**Files created/modified:**
- [Dockerfile](Dockerfile) - Multi-stage build với curl cho healthcheck

---

## TASK-OPS-02: Docker Compose + Volume ✅

**Mục tiêu:** Hoàn thiện `docker-compose.yml` — single service + persistent volume.

**Checklist:**
- [x] Review `docker-compose.yml` hiện tại
- [x] Mount volume `./data:/app/data` (SQLite + ChromaDB persist)
- [x] Mount volume `./.ai-log:/app/.ai-log` (AI prompt log)
- [x] Env vars từ `.env` (hoặc inline defaults)
- [x] Auto-restart policy (`restart: unless-stopped`)
- [x] Port mapping `8000:8000`
- [x] Health check trong compose (`healthcheck:` block)
- [x] Start period configuration

**Files created/modified:**
- [docker-compose.yml](docker-compose.yml) - Thêm volumes, healthcheck, environment

---

## TASK-OPS-03: Makefile targets (run/test/lint/backup) ✅

**Mục tiêu:** Mở rộng Makefile — bổ sung các target tiện ích.

**Checklist:**
- [x] Review Makefile hiện tại
- [x] Thêm target `make backup` → gọi `scripts/backup.sh`
- [x] Thêm target `make restore` → gọi `scripts/restore.sh`
- [x] Thêm target `make logs` → `docker compose logs -f`
- [x] Thêm target `make shell` → `docker compose exec backend bash`
- [x] Thêm target `make migrate` → `alembic upgrade head`
- [x] Thêm target `make seed` → `python scripts/seed.py`
- [x] Thêm target `make test` → `pytest tests/`
- [x] Thêm target `make lint` → `ruff check src/`
- [x] Thêm target `make format` → `ruff format src/`
- [x] Thêm target `make typecheck` → `mypy src/`
- [x] Thêm target `make clean` → xoá `__pycache__`, `.pytest_cache`, etc.
- [x] Thêm target `make help` → hiển thị danh sách commands
- [x] Thêm target `make health` → kiểm tra health endpoint

**Files created/modified:**
- [Makefile](Makefile) - Mở rộng với ~20 targets

---

## TASK-OPS-04: Scripts (backup.sh + restore.sh + seed.py) ✅

**Mục tiêu:** Tạo các script tiện ích cho backup, restore, seed data.

**Checklist:**
- [x] Tạo `scripts/backup.sh` — `tar -czf backup/data-$(date +%Y%m%d-%H%M%S).tar.gz ./data/`
- [x] Tạo `scripts/restore.sh` — extract từ file backup vào `./data/`
- [x] Tạo `scripts/seed.py` — tạo user demo + Contact mẫu + Conversation mẫu + Memory mẫu
  - Demo user: `demo@example.com` / `demo123`
  - 5 Contact: Nguyễn Văn A (giáo viên), Trần Thị B (lập trình viên), Lê Văn C (bác sĩ), Phạm Thị D (kế toán), Hoàng Văn E (kiến trúc sư)
  - 5 Conversation mẫu
  - 5 ContactMemory mẫu
- [x] Verify scripts chạy được cả local và trong Docker container

**Files created:**
- [scripts/backup.sh](scripts/backup.sh) - Backup script với timestamp
- [scripts/restore.sh](scripts/restore.sh) - Restore script với dry-run support
- [scripts/seed.py](scripts/seed.py) - Seed script với demo data

---

## TASK-OPS-05: Health check + Structured logging ✅

**Mục tiêu:** Health endpoint + JSON logging chuẩn production.

**Checklist:**
- [x] Endpoint `GET /health` — trả 200 OK + `{ status: "ok", version: "1.0-mvp", db: "ok" }`
- [x] Check DB connection trong `/health`
- [x] Cấu hình `structlog` cho JSON output (stdout + file `.ai-log/app.log`)
- [x] Log request ID cho mỗi request (middleware tạo UUID + attach vào context)
- [x] Log AI prompt + response riêng vào `.ai-log/ai-{date}.jsonl`
- [x] Log level config từ env: `LOG_LEVEL=INFO`
- [x] Verify log JSON parse được bằng `jq`

**Files created/modified:**
- [src/core/logging.py](src/core/logging.py) - Structured logging module
- [src/core/middlewares.py](src/core/middlewares.py) - Request logging middleware với request ID
- [src/main.py](src/main.py) - Health endpoint và logging setup
- [requirements.txt](requirements.txt) - Thêm structlog

**Verified:**
```bash
$ curl http://localhost:8000/health
{"status":"ok","version":"1.0.0-mvp","db":"ok"}
```

---

## Verification

```bash
# 1. Build Docker image
docker build -t memorychat:latest .

# 2. Start services
docker compose up -d

# 3. Verify health
curl http://localhost:8000/health

# 4. Run tests (158 tests pass)
make test

# 5. Seed data
make seed

# 6. Create backup
make backup

# 7. Check logs
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
✅ Log JSON chuẩn cho mỗi request (parse được bằng jq)
✅ .ai-log/ chứa JSON Lines của AI prompt + response
✅ Seed data tạo user demo + 5 Contact + 5 Conversation mẫu
✅ Tài liệu trong README đầy đủ
```

---

## Files Changed Summary

| File | Change |
|------|--------|
| `Dockerfile` | Multi-stage build, non-root user, curl for healthcheck |
| `docker-compose.yml` | Volumes, healthcheck, environment |
| `Makefile` | 20+ targets for dev ops |
| `.env.example` | Updated with current config |
| `.gitignore` | Keep data/backup directories structure |
| `requirements.txt` | Added structlog |
| `src/main.py` | Health endpoint với DB check, logging setup |
| `src/core/logging.py` | NEW - Structured logging module |
| `src/core/middlewares.py` | Request ID tracking, structured logging |
| `scripts/backup.sh` | NEW - Backup script |
| `scripts/restore.sh` | NEW - Restore script với dry-run |
| `scripts/seed.py` | NEW - Seed script với 5 demo contacts |
| `data/.gitkeep` | NEW - Preserve data directory |
| `backup/.gitkeep` | NEW - Preserve backup directory |
