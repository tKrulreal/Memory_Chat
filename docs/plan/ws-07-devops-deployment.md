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

- ✅ `Dockerfile` (có sẵn từ AI20K template).
- ✅ `docker-compose.yml` (có sẵn).
- ✅ `Makefile` (có sẵn).
- ✅ `.env.example` (có sẵn).
- ⬜ Health check endpoint chưa có.
- ⬜ Structured logging chưa config.
- ⬜ Backup/restore script chưa có.
- ⬜ Seed script chưa có.

---

## TASK-OPS-01: Dockerfile review + multi-stage ⬜

**Mục tiêu:** Hoàn thiện Dockerfile — multi-stage build, non-root user, pinned version.

**Checklist:**
- [ ] Review Dockerfile hiện tại
- [ ] Multi-stage build (builder stage + runtime stage)
- [ ] Non-root user trong container (`user app`)
- [ ] Pin Python version 3.11-slim
- [ ] Cài `requirements.txt` từ freeze
- [ ] `HEALTHCHECK` directive (gọi `/health` mỗi 30s)
- [ ] Copy source code sau khi install deps (tận dụng cache)
- [ ] Giảm image size (no cache, clean apt)

**Commands:**
```bash
# Build
docker build -t memorychat:latest .

# Verify size
docker images memorychat:latest
```

---

## TASK-OPS-02: Docker Compose + Volume ⬜

**Mục tiêu:** Hoàn thiện `docker-compose.yml` — single service + persistent volume.

**Checklist:**
- [ ] Review `docker-compose.yml` hiện tại
- [ ] Mount volume `./data:/app/data` (SQLite + ChromaDB persist)
- [ ] Mount volume `./.ai-log:/app/.ai-log` (AI prompt log)
- [ ] Env vars từ `.env` (hoặc inline defaults)
- [ ] Auto-restart policy (`restart: unless-stopped`)
- [ ] Port mapping `8000:8000`
- [ ] Health check trong compose (`healthcheck:` block)
- [ ] Optional: Caddy reverse proxy service (Caddyfile cho HTTPS local)

**Commands:**
```bash
# Khởi động
docker compose up -d

# Verify
docker compose ps
curl http://localhost:8000/health
```

---

## TASK-OPS-03: Makefile targets (run/test/lint/backup) ⬜

**Mục tiêu:** Mở rộng Makefile — bổ sung các target tiện ích.

**Checklist:**
- [ ] Review Makefile hiện tại
- [ ] Thêm target `make backup` → gọi `scripts/backup.sh`
- [ ] Thêm target `make restore` → gọi `scripts/restore.sh`
- [ ] Thêm target `make logs` → `docker compose logs -f`
- [ ] Thêm target `make shell` → `docker compose exec api bash`
- [ ] Thêm target `make migrate` → `alembic upgrade head`
- [ ] Thêm target `make seed` → `python scripts/seed.py`
- [ ] Thêm target `make test` → `pytest tests/`
- [ ] Thêm target `make lint` → `ruff check src/`
- [ ] Thêm target `make format` → `ruff format src/`
- [ ] Thêm target `make typecheck` → `mypy src/`
- [ ] Thêm target `make clean` → xoá `__pycache__`, `.pytest_cache`, etc.

**Commands:**
```bash
make help
make run
make test
make backup
make logs
```

---

## TASK-OPS-04: Scripts (backup.sh + restore.sh + seed.py) ⬜

**Mục tiêu:** Tạo các script tiện ích cho backup, restore, seed data.

**Checklist:**
- [ ] Tạo `scripts/backup.sh` — `tar -czf backup/data-$(date +%Y%m%d-%H%M%S).tar.gz ./data/`
- [ ] Tạo `scripts/restore.sh` — extract từ file backup vào `./data/`
- [ ] Tạo `scripts/seed.py` — tạo user demo + Contact mẫu + Conversation mẫu + Memory mẫu
  - Demo user: `demo@example.com` / `demo123`
  - 5 Contact: "Nguyễn Văn A" (giáo viên), "Trần Thị B" (lập trình viên), "Lê Văn C" (bác sĩ), ...
  - 5 Conversation mẫu
  - 5 ContactMemory mẫu
- [ ] Verify scripts chạy được cả local và trong Docker container

**Commands:**
```bash
make backup
make restore
make seed

# Verify
ls -la backup/
sqlite3 data/app.db "SELECT COUNT(*) FROM contact;"
```

---

## TASK-OPS-05: Health check + Structured logging ⬜

**Mục tiêu:** Health endpoint + JSON logging chuẩn production.

**Checklist:**
- [ ] Endpoint `GET /health` — trả 200 OK + `{ status: "ok", version: "1.0-mvp", db: "ok" }`
- [ ] Check DB connection trong `/health`
- [ ] Cấu hình `structlog` cho JSON output (stdout + file `.ai-log/app.log`)
- [ ] Log request ID cho mỗi request (middleware tạo UUID + attach vào context)
- [ ] Log AI prompt + response riêng vào `.ai-log/ai-{date}.jsonl`
- [ ] Log level config từ env: `LOG_LEVEL=INFO`
- [ ] Verify log JSON parse được bằng `jq`

**Commands:**
```bash
# Test health
curl http://localhost:8000/health

# Test log JSON
curl http://localhost:8000/api/v1/contacts -H "Authorization: Bearer $TOKEN"
# Check log file
cat .ai-log/app.log | tail -1 | jq .
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
