# Member 1 — Backend + DevOps (Leader)

> **Phụ trách:** WS-01 (Backend Foundation) + WS-07 (DevOps & Deployment) + hỗ trợ Member 3, 4 khi có vấn đề Backend.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | Tuần 1 → Tuần 6 |
| Độ phức tạp | 🟡 Trung bình |
| Phụ thuộc | Spec + Plan |
| Unblock | Member 2 (FE), Member 3 (BE), Member 4 (AI) |

---

## Module của Member 1 (6 modules)

| Module | Mô tả | Tuần |
|--------|-------|------|
| **M1-BE-01** | DB Schema + Migration (11 models + Alembic) | Tuần 2 ✅ |
| **M1-BE-02** | Repository + Service Layer (8 repos + 5 services) | Tuần 2 ✅ / Tuần 3 |
| **M1-BE-03** | Auth (JWT) + LLM Gateway (retry + log + embed) | Tuần 3 |
| **M1-BE-04** | API Skeleton (routers + middleware + Tests) | Tuần 3 / Tuần 4 |
| **M1-BE-05** | Docker (Dockerfile + Compose) + Scripts (backup, seed) | Tuần 4 |
| **M1-BE-06** | Demo Material (Slide + Health + Logging) | Tuần 5 |

---

## Trạng thái hiện tại (cập nhật 03/08/2026)

- ✅ Đã đọc spec + plan.
- ✅ Setup môi trường Python 3.11 + Docker + OpenAI key.
- ✅ **GATE 1 đã nộp 02/08** (Chủ nhật tuần 2).
- ✅ M1-BE-01 (DB Schema + Migration) xong.
- ✅ M1-BE-02 (Repo+Service skeleton) xong.
- 🟡 **Đang vào tuần 3** — M1-BE-03 (Auth + LLM Gateway).
- ⬜ M1-BE-04 → M1-BE-06 đang pending.

---

## Tuần 1 (23/07 – 29/07) ✅

- [x] Đọc `docs/general overview/01_Project_Overview.md` → `10_Roadmap_Development.md`
- [x] Đọc `docs/plan/README.md` + `ws-01-backend-foundation.md`
- [x] Cài Python 3.11, pip, virtualenv
- [x] Cài Docker Desktop + test `docker run hello-world`
- [x] Lấy `OPENAI_API_KEY` từ https://platform.openai.com/
- [x] Test gọi OpenAI API thành công (`gpt-4o-mini`)
- [x] Tạo `.env` local với `OPENAI_API_KEY=sk-...`
- [x] Setup git + push lên GitHub

---

## Tuần 2 (30/07 – 02/08) ✅ — GATE 1

### Module M1-BE-01: DB Schema + Migration ✅
- [x] 11 models (User, Contact, Conversation, Message, ContactMemory, Recommendation, Tag, ContactTag, SearchHistory, Notification, Setting, EventLog)
- [x] `alembic init` + migration đầu tiên
- [x] `alembic upgrade head` chạy thành công trên SQLite
- [x] Verify 11 bảng đã tạo (`sqlite3 data/app.db ".tables"`)

### Module M1-BE-02 (phần 1): Repository + Service skeleton ✅
- [x] `BaseRepository` (CRUD generic)
- [x] ConversationRepository, MessageRepository, ContactRepository
- [x] ContactService, ConversationService, MessageService skeleton

### 🚨 GATE 1 (02/08 CN) ✅
- [x] **Demo trên Swagger:** 11 bảng migrate → CRUD qua ORM
- [x] Frontend Member 2 + Member 3 test API Contact thành công
- [x] Nộp GATE 1 ngày **02/08 (Chủ nhật)**

---

## Tuần 3 (03/08 – 09/08) 🟡

### Module M1-BE-03: Auth + LLM Gateway

- [ ] **AuthService** (register, login, verify_token — hash password bằng bcrypt)
- [ ] Middleware `get_current_user` (FastAPI Depends)
- [ ] API `POST /api/v1/auth/register` + `POST /api/v1/auth/login`
- [ ] JWT với `python-jose`, secret từ env `JWT_SECRET`, expire 60 phút
- [ ] **LLMGateway** class với retry + exponential backoff (max 3 lần)
- [ ] Method `complete()`, `chat()`, `embed()`
- [ ] Log prompt + response vào `.ai-log/` (JSON Lines)
- [ ] Timeout config từ env: `LLM_TIMEOUT=30`

### Module M1-BE-04 (phần 1): API Skeleton

- [ ] Tạo skeleton routers: contacts, conversations, messages, memory, recommendations, search, copilot
- [ ] Include tất cả router trong `main.py` với prefix `/api/v1`
- [ ] CORS middleware (cho Frontend `localhost:5173`)
- [ ] Global exception handler + Request logging middleware
- [ ] Settings (Pydantic BaseSettings) + `.env.example` đầy đủ

### 🎯 MVP (09/08 CN)
- [ ] **Demo Backend:** Auth + LLM + full Swagger hiển thị endpoints
- [ ] Member 3 + 4 có thể tích hợp Memory Agent + ChromaDB
- [ ] Verify: `make run` + `curl /docs` + register/login flow OK

---

## Tuần 4 (10/08 – 16/08) ⬜

### Module M1-BE-04 (phần 2): Tests

- [ ] Setup `tests/` folder + `conftest.py` (fixture DB in-memory SQLite)
- [ ] Unit test cho tất cả Repository + Service layer (mock LLM)
- [ ] Unit test Auth (register, login, JWT, password sai → 401)
- [ ] pytest-cov config + target coverage > 70%

### Module M1-BE-05: Docker + Scripts

- [ ] **Dockerfile** (multi-stage build, Python 3.11 pinned, non-root user)
- [ ] **docker-compose.yml** (mount volumes cho data/ + .ai-log/, health check)
- [ ] **Makefile** targets: `setup`, `run`, `test`, `migrate`, `seed`, `backup`, `restore`, `logs`, `shell`
- [ ] `scripts/backup.sh` + `scripts/restore.sh` (zip data/ → backup/)
- [ ] `scripts/seed.py` (1 user + 5 Contact mẫu)

### 🚨 GATE 2 (16/08 CN)
- [ ] **Demo:** Backend chạy trong Docker + Makefile `make run` + `make test` pass
- [ ] Member 4 có Copilot + Search + Recommendation hoạt động end-to-end
- [ ] Verify `docker compose up` → app chạy port 8000 OK

---

## Tuần 5 (17/08 – 23/08) ⬜

### Module M1-BE-06: Demo Material

- [ ] Endpoint `GET /health` (return JSON: status, version, db, chroma)
- [ ] Structlog JSON config + Request ID middleware
- [ ] Log AI prompt/response ra `.ai-log/YYYY-MM-DD.jsonl`
- [ ] **Slide (13 slides):**
  - Slide 1: Tên dự án MemoryChat
  - Slide 2: Vấn đề (mất context khi reconnect)
  - Slide 3: Giải pháp (AI Memory + Relationship Intelligence)
  - Slide 4: Tech Stack (FastAPI + LangGraph + OpenAI + SQLite + ChromaDB)
  - Slide 5: Architecture diagram
  - Slide 6: Database schema (11 bảng)
  - Slide 7: AI Workflow (Memory → Search → Recommendation)
  - Slide 8: Backend API overview (Swagger screenshot)
- [ ] Final commit `v1.0-mvp` tag + Nộp slide + video

---

## Tuần 6 (24/08 – 01/09) ⬜

- [ ] **T2 (25/08):** Rehearsal lần 1 (5 phút demo) — ghi nhận feedback
- [ ] **T4 (27/08):** Rehearsal lần 2 — target chạy trơn tru 5 phút
- [ ] **T5 (28/08):** Rehearsal lần 3 — target chạy trơn tru 5 phút
- [ ] **T6 (29/08):** Final rehearsal + backup `data/` + chuẩn bị laptop
- [ ] **T2 (01/09) 🏆 DEMO DAY:** Demo 5 phút + Q&A với BGK

---

## ✅ Checklist cuối cùng (Tuần 6)

```
✅ M1-BE-01 → M1-BE-06 (6 modules)              → DONE
✅ 11 bảng DB migrated                          → OK
✅ Repository + Service + Auth + LLM Gateway    → OK
✅ make run / make test / make backup           → OK
✅ docker compose up                            → OK
✅ Test coverage > 70%                          → OK
✅ Slide 13 trang + Video 3 phút                → OK
✅ Demo Day 01/09/2026                          → OK
```

---

## ⚠️ Vướng mắc

| Ngày | Vấn đề | Giải pháp |
|------|--------|-----------|
| (chưa có) | | |