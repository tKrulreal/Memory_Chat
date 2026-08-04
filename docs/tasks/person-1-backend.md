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

## Trạng thái hiện tại

- ✅ Đã đọc spec + plan.
- ✅ Setup môi trường Python 3.11 + Docker + OpenAI key.
- 🟡 Đang vào tuần 2 — GATE 1.
- ⬜ WS-01 chưa bắt đầu code models.

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

## Tuần 2 (30/07 – 05/08) 🟡 — GATE 1

> **Mốc:** 05/08 demo Backend chạy được trên Swagger.

### T2 (30/07)
- [ ] TASK-BE-01: Model `User` (id, email, password_hash, created_at)
- [ ] TASK-BE-01: Model `Contact` (id, user_id, name, avatar_url, relationship_score)
- [ ] TASK-BE-01: Model `Conversation` (id, contact_id, user_id, title, last_message_at, status)

### T3 (31/07)
- [ ] TASK-BE-01: Model `Message` (id, conversation_id, sender, content, role, created_at)
- [ ] TASK-BE-01: Model `ContactMemory` (id, contact_id, summary, timeline JSON, company, profession, skills, interests, relationship_score)
- [ ] TASK-BE-01: Model `Recommendation` (id, contact_id, type, reason, status)

### T4 (01/08)
- [ ] TASK-BE-01: Model `Tag` + `ContactTag`
- [ ] TASK-BE-01: Model `SearchHistory` + `Notification` + `Setting`
- [ ] TASK-BE-01: Model `EventLog`
- [ ] TASK-BE-02: `alembic init alembic`

### T5 (02/08)
- [ ] TASK-BE-02: Cấu hình `alembic/env.py` trỏ tới `src.models.Base.metadata`
- [ ] TASK-BE-02: Tạo migration đầu tiên `alembic revision --autogenerate -m "init schema"`
- [ ] TASK-BE-02: Test `alembic upgrade head` chạy thành công
- [ ] TASK-BE-03: Tạo `src/repositories/base.py` (BaseRepository skeleton)

### T6 (03/08)
- [ ] TASK-BE-03: ConversationRepository (CRUD + list_by_user)
- [ ] TASK-BE-03: MessageRepository (CRUD + list_by_conversation)
- [ ] TASK-BE-03: ContactRepository (CRUD + get_by_user)

### CN (04/08) — optional
- [ ] Buffer: fix bug, review code
- [ ] Help Member 3 nếu cần

### T2 (05/08) 🚨 **GATE 1**
- [ ] **Demo trên Swagger:** 11 bảng đã migrate → User có thể insert qua ORM
- [ ] Verify: `sqlite3 data/app.db ".tables"` → 11 bảng
- [ ] Cập nhật `timeline.md` tuần 2

---

## Tuần 3 (06/08 – 12/08) ⬜

### T2 (06/08)
- [ ] TASK-BE-03: MemoryRepository + RecommendationRepository
- [ ] TASK-BE-03: EventLogRepository + UserRepository

### T3 (07/08)
- [ ] TASK-BE-04: ContactService + ConversationService
- [ ] TASK-BE-04: MessageService + MemoryService

### T4 (08/08)
- [ ] TASK-BE-05: LLMGateway class với retry + log
- [ ] TASK-BE-05: Test `complete()`, `chat()`, `embed()`

### T5 (09/08)
- [ ] TASK-BE-06: AuthService (register, login, verify_token)
- [ ] TASK-BE-06: Middleware `get_current_user`

### T6 (10/08)
- [ ] TASK-BE-06: API `POST /auth/register` + `POST /auth/login`
- [ ] TASK-BE-07: Settings (Pydantic BaseSettings)

### CN (11/08) — optional
- [ ] TASK-BE-08: Tạo skeleton routers cho tất cả module
- [ ] TASK-BE-08: Include routers trong `main.py`

### T2 (12/08) 🎯 **MVP**
- [ ] **Demo:** Backend có đầy đủ CRUD + Auth + LLM Gateway + Swagger docs
- [ ] Member 3 + 4 có thể tích hợp Memory Agent + ChromaDB
- [ ] Cập nhật `timeline.md` tuần 3

---

## Tuần 4 (13/08 – 19/08) ⬜

### T2 (13/08)
- [ ] TASK-BE-09: Unit test Repository + Service (test_basic_crud)
- [ ] TASK-BE-09: pytest-cov config

### T3 (14/08)
- [ ] TASK-BE-09: Test MessageService + MemoryService (mock LLM)
- [ ] TASK-BE-10: Unit test Auth (register, login, JWT)

### T4 (15/08)
- [ ] TASK-BE-11: Cập nhật `.env.example` đầy đủ
- [ ] TASK-BE-11: Document env vars trong README

### T5 (16/08)
- [ ] TASK-OPS-01: Review Dockerfile + multi-stage build
- [ ] TASK-OPS-01: Non-root user + pinned Python 3.11

### T6 (17/08)
- [ ] TASK-OPS-02: Review `docker-compose.yml` + mount volumes
- [ ] TASK-OPS-02: Health check trong compose

### CN (18/08) — optional
- [ ] Buffer

### T2 (19/08) 🚨 **GATE 2**
- [ ] **Demo:** Backend chạy trong Docker + Makefile `make run` + `make test` pass
- [ ] Member 4 có Copilot + Search + Recommendation hoạt động end-to-end

---

## Tuần 5 (20/08 – 26/08) ⬜

### T2 (20/08)
- [ ] TASK-OPS-03: Makefile targets (backup, restore, logs, shell, seed, migrate)
- [ ] TASK-OPS-04: `scripts/backup.sh` + `scripts/restore.sh`

### T3 (21/08)
- [ ] TASK-OPS-04: `scripts/seed.py` (1 user + 5 Contact mẫu)
- [ ] TASK-OPS-04: Verify seed data trong `data/app.db`

### T4 (22/08)
- [ ] TASK-OPS-05: Endpoint `GET /health` + JSON response
- [ ] TASK-OPS-05: Structlog JSON config

### T5 (23/08)
- [ ] TASK-OPS-05: Request ID middleware + log AI prompt
- [ ] TASK-TEST-01: Hoàn thiện test suite (target coverage > 70%)

### T6 (24/08)
- [ ] Slide (slides 1-5): Tên dự án, Vấn đề, Giải pháp, Tech Stack, Architecture
- [ ] Slide (slides 6-8): Database schema, AI Workflow, Backend API

### CN (25/08) — optional
- [ ] Slide (slides 9-13): Frontend, Use cases, Roadmap, Team, Q&A

### T2 (26/08) — **Nộp hồ sơ Demo Day**
- [ ] Final commit `v1.0-mvp` tag
- [ ] Verify slide + video

---

## Tuần 6 (27/08 – 01/09) ⬜

### T2 (27/08)
- [ ] Rehearsal lần 1 (toàn nhóm) — 5 phút demo
- [ ] Ghi nhận feedback

### T4 (29/08)
- [ ] Rehearsal lần 2 — target chạy trơn tru 5 phút

### T5 (30/08)
- [ ] Rehearsal lần 3 — target chạy trơn tru 5 phút

### T6 (31/08)
- [ ] Final rehearsal + Backup data
- [ ] Chuẩn bị: laptop + demo script in sẵn

### T2 (01/09) 🏆 **DEMO DAY**
- [ ] Setup trước 30 phút
- [ ] Demo 5 phút
- [ ] Q&A với BGK

---

## ✅ Checklist cuối cùng

```
Tất cả TASK-BE-* (12 tasks)        → STATUS
Tất cả TASK-OPS-* (5 tasks)        → STATUS
Tất cả TASK-TEST-* (5 tasks, hỗ trợ Member 3/4)
make run                             → OK
make test                            → OK
make backup                          → OK
docker compose up                    → OK
Coverage > 70%                       → OK
```

---

## ⚠️ Vướng mắc

| Ngày | Vấn đề | Giải pháp |
|------|--------|-----------|
| (chưa có) | | |
