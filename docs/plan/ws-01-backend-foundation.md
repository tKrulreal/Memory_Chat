# WS-01 — Backend Foundation

> **Mục tiêu:** Thiết lập nền tảng Backend — ORM, Schema, Settings, Auth skeleton, LLM Gateway chuẩn hoá.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | WS-01 (đầu tiên) |
| Độ phức tạp | 🟡 Trung bình |
| Phụ thuộc | Không có |
| Unblock | WS-02, WS-03, WS-04, WS-05, WS-06 |

---

## Trạng thái hiện tại

- ✅ `src/main.py` skeleton (FastAPI app + lifespan).
- ✅ `src/services/llm.py` skeleton (LLM Gateway placeholder).
- ✅ `src/agents/graph.py` skeleton (LangGraph `analyze` + `respond`).
- ✅ `src/api/chat.py` router (gọi LangGraph).
- ⬜ Models, Repositories, Services chưa có.
- ⬜ Alembic chưa init.
- ⬜ Auth skeleton chưa có.

---

## TASK-BE-01: Database Models (SQLAlchemy) ⬜

**Mô tả:** Định nghĩa 11 bảng schema theo `docs/general overview/04_Database_Design.md`.

**Checklist:**
- [ ] Tạo `src/models/__init__.py` + base class `Base` (SQLAlchemy 2.x DeclarativeBase)
- [ ] Model `User` (id, email, password_hash, created_at)
- [ ] Model `Contact` (id, user_id, name, avatar_url, relationship_score)
- [ ] Model `Conversation` (id, contact_id, user_id, title, last_message_at, status)
- [ ] Model `Message` (id, conversation_id, sender, content, role, created_at)
- [ ] Model `ContactMemory` (id, contact_id, summary, timeline JSON, company, profession, skills, interests, relationship_score, updated_at)
- [ ] Model `Recommendation` (id, contact_id, type, reason, status, created_at)
- [ ] Model `Tag` (id, name) + `ContactTag` (contact_id, tag_id)
- [ ] Model `SearchHistory` (id, user_id, query, results JSON, created_at)
- [ ] Model `Notification` (id, user_id, type, payload JSON, read_at)
- [ ] Model `Setting` (id, user_id, key, value JSON)
- [ ] Model `EventLog` (id, user_id, event_type, payload JSON, created_at)

**Commands:**
```bash
mkdir -p src/models
touch src/models/__init__.py
# Tạo từng file model
```

---

## TASK-BE-02: Alembic Migration ⬜

**Mô tả:** Khởi tạo Alembic và tạo migration đầu tiên cho toàn bộ schema.

**Checklist:**
- [ ] `alembic init alembic`
- [ ] Cấu hình `alembic.ini` + `alembic/env.py` trỏ tới `src.models.Base.metadata`
- [ ] Cấu hình `DATABASE_URL` từ `.env`
- [ ] Tạo `alembic/versions/<hash>_init_schema.py`
- [ ] Verify migration chạy được trên SQLite trống: `alembic upgrade head`
- [ ] Verify 11 bảng đã được tạo

**Commands:**
```bash
alembic init alembic
alembic revision --autogenerate -m "init schema"
alembic upgrade head
sqlite3 data/app.db ".tables"
```

---

## TASK-BE-03: Repositories (CRUD layer) ⬜

**Mô tả:** Implement Repository pattern cho mỗi model — đóng gói logic truy vấn DB.

**Checklist:**
- [ ] Tạo `src/repositories/base.py` (BaseRepository generic với CRUD: `get`, `list`, `create`, `update`, `delete`)
- [ ] `ConversationRepository` (CRUD + `list_by_user`)
- [ ] `MessageRepository` (CRUD + `list_by_conversation`)
- [ ] `ContactRepository` (CRUD + `get_by_user`)
- [ ] `MemoryRepository` (CRUD + `get_by_contact`)
- [ ] `RecommendationRepository` (CRUD + `list_pending`)
- [ ] `EventLogRepository` (CRUD + `list_recent`)
- [ ] `UserRepository` (CRUD + `get_by_email`)
- [ ] `TagRepository` + `ContactTagRepository`
- [ ] `SearchHistoryRepository` + `NotificationRepository` + `SettingRepository`

**Commands:**
```bash
mkdir -p src/repositories
# Implement từng repository
pytest tests/unit/repositories -v
```

---

## TASK-BE-04: Services (business logic) ⬜

**Mô tả:** Service layer gọi Repository + áp dụng business rules.

**Checklist:**
- [ ] `src/services/contact.py` (ContactService — CRUD qua repo)
- [ ] `src/services/conversation.py` (ConversationService — CRUD + logic mở/đóng)
- [ ] `src/services/message.py` (MessageService — CRUD + emit Event `SEND_MESSAGE`)
- [ ] `src/services/memory.py` (MemoryService — CRUD + trigger Memory Agent)
- [ ] `src/services/recommendation.py` (RecommendationService — CRUD + accept/reject)
- [ ] `src/services/event_log.py` (EventLogService — ghi log event)
- [ ] Tất cả Service inject Repository qua constructor (DI)

**Commands:**
```bash
mkdir -p src/services
pytest tests/unit/services -v
```

---

## TASK-BE-05: LLM Gateway (retry + log) ⬜

**Mô tả:** Chuẩn hoá `src/services/llm.py` thành LLM Gateway có retry, logging, fallback.

**Checklist:**
- [ ] Refactor `src/services/llm.py` thành class `LLMGateway`
- [ ] Method `complete(prompt, **kwargs) -> str`
- [ ] Method `chat(messages, **kwargs) -> str`
- [ ] Method `embed(text) -> list[float]`
- [ ] Retry với exponential backoff (max 3 lần)
- [ ] Log prompt + response vào `.ai-log/` (JSON Lines)
- [ ] Timeout config từ env: `LLM_TIMEOUT=30`
- [ ] Fallback graceful error (không crash app)

**Commands:**
```bash
# Test LLM Gateway
python -c "from src.services.llm import LLMGateway; g = LLMGateway(); print(g.complete('Hello'))"
```

---

## TASK-BE-06: Auth (JWT + bcrypt) ⬜

**Mô tả:** Implement AuthService + middleware xác thực JWT.

**Checklist:**
- [ ] `src/services/auth.py` (AuthService — register, login, verify_token)
- [ ] Hash password bằng `passlib[bcrypt]`
- [ ] Sinh JWT bằng `python-jose` với secret từ env: `JWT_SECRET`
- [ ] Middleware `get_current_user` (FastAPI Depends)
- [ ] Endpoint `POST /api/v1/auth/register` (create User)
- [ ] Endpoint `POST /api/v1/auth/login` (return access_token)
- [ ] Token expire: `JWT_EXPIRE_MINUTES=60`
- [ ] Optional: bỏ qua auth trong demo (1 user cố định)

**Commands:**
```bash
# Test register + login
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demo123"}'

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demo123"}'
```

---

## TASK-BE-07: Settings + Config ⬜

**Mô tả:** Chuẩn hoá `src/config.py` (hoặc `src/core/settings.py`) — load env vars + validate.

**Checklist:**
- [ ] Dùng Pydantic Settings (`BaseSettings`)
- [ ] Vars bắt buộc: `OPENAI_API_KEY`, `DATABASE_URL`, `JWT_SECRET`
- [ ] Vars optional: `LLM_MODEL`, `EMBEDDING_MODEL`, `LLM_TIMEOUT`, `LOG_LEVEL`
- [ ] Validate `OPENAI_API_KEY` không rỗng khi khởi động
- [ ] Singleton instance: `settings = Settings()`
- [ ] Tạo `.env.example` đầy đủ
- [ ] Document từng biến env trong README

**Commands:**
```bash
cp .env.example .env
# Điền OPENAI_API_KEY=sk-...
python -c "from src.config import settings; print(settings.OPENAI_API_KEY[:10])"
```

---

## TASK-BE-08: Middleware + Routers ⬜

**Mô tả:** Kết nối các thành phần vào `src/main.py` — include routers + middleware.

**Checklist:**
- [ ] Tạo `src/api/contacts.py` (router cho Contact API — placeholder)
- [ ] Tạo `src/api/conversations.py` (router placeholder)
- [ ] Tạo `src/api/messages.py` (router placeholder)
- [ ] Tạo `src/api/memory.py` (router placeholder)
- [ ] Tạo `src/api/recommendations.py` (router placeholder)
- [ ] Tạo `src/api/search.py` (router placeholder)
- [ ] Tạo `src/api/copilot.py` (router placeholder)
- [ ] Cập nhật `src/main.py` include tất cả router
- [ ] Mount `/api/v1` prefix
- [ ] CORS middleware (cho Frontend)
- [ ] Global exception handler
- [ ] Request logging middleware

**Commands:**
```bash
# Khởi động server
make run

# Verify Swagger
curl http://localhost:8000/docs
```

---

## TASK-BE-09: Unit tests cho Repository + Service ⬜

**Mô tả:** Unit test cho từng Repository + Service layer.

**Checklist:**
- [ ] Setup `tests/` folder + `conftest.py` (fixture DB in-memory SQLite)
- [ ] Test `ConversationRepository` (CRUD + list_by_user)
- [ ] Test `MessageRepository` (CRUD + list_by_conversation)
- [ ] Test `ContactRepository` (CRUD + get_by_user)
- [ ] Test `MemoryRepository` (CRUD + get_by_contact)
- [ ] Test `RecommendationRepository` (CRUD + list_pending)
- [ ] Test `EventLogRepository` (CRUD + list_recent)
- [ ] Test `ContactService` (logic nghiệp vụ)
- [ ] Test `MessageService` (logic + emit event)
- [ ] Test `MemoryService` (logic + trigger agent)

**Commands:**
```bash
mkdir -p tests/unit/repositories tests/unit/services
pytest tests/unit -v --cov=src/repositories --cov=src/services
```

---

## TASK-BE-10: Unit test Auth ⬜

**Mô tả:** Unit test cho AuthService + API endpoints.

**Checklist:**
- [ ] Test `AuthService.register` (hash password + tạo User)
- [ ] Test `AuthService.login` (verify password + sinh JWT)
- [ ] Test `AuthService.verify_token` (decode JWT + trả user)
- [ ] Test API `POST /auth/register` (200 + trả user_id)
- [ ] Test API `POST /auth/login` (200 + trả access_token)
- [ ] Test API `POST /auth/login` với password sai (401)
- [ ] Test API `/contacts` với token hợp lệ (200)
- [ ] Test API `/contacts` không có token (401)

**Commands:**
```bash
pytest tests/unit/auth tests/api/test_auth.py -v
```

---

## TASK-BE-11: Cập nhật `.env.example` ⬜

**Mô tả:** Bổ sung đầy đủ biến env cần thiết cho toàn bộ Backend.

**Checklist:**
- [ ] `OPENAI_API_KEY` (bắt buộc)
- [ ] `DATABASE_URL=sqlite:///./data/app.db`
- [ ] `CHROMA_PERSIST_DIR=./data/chroma`
- [ ] `JWT_SECRET=change-me-in-production`
- [ ] `JWT_EXPIRE_MINUTES=60`
- [ ] `LLM_MODEL=gpt-4o-mini`
- [ ] `EMBEDDING_MODEL=text-embedding-3-small`
- [ ] `LLM_TIMEOUT=30`
- [ ] `LOG_LEVEL=INFO`
- [ ] `LOG_DIR=./.ai-log`
- [ ] `CORS_ORIGINS=http://localhost:5173`

**Commands:**
```bash
cp .env.example .env
# Sửa .env với OPENAI_API_KEY thật
```

---

## TASK-BE-12: Cập nhật README ⬜

**Mô tả:** Cập nhật `README.md` chính của dự án — hướng dẫn setup + chạy migration.

**Checklist:**
- [ ] Section "Quick Start" (clone → make setup → make run)
- [ ] Section "Architecture" (liên kết tới `docs/general overview/05_Backend_Architecture.md`)
- [ ] Section "Tech Stack" (MVP)
- [ ] Section "Environment Variables" (tham chiếu `.env.example`)
- [ ] Section "Database Migration" (alembic upgrade head)
- [ ] Section "Running Tests" (pytest)
- [ ] Section "Project Structure" (folder tree)

**Commands:**
```bash
# Verify README render đúng trên GitHub
cat README.md
```

---

## Kết quả mong đợi sau WS-01

```
✅ 11 bảng DB đã migrate thành công
✅ Alembic upgrade head chạy trên SQLite trống
✅ Repository + Service layer đầy đủ + có unit test
✅ LLM Gateway có retry + log
✅ Auth register + login trả JWT hợp lệ
✅ Tất cả router được include trong main.py
✅ Swagger UI tại /docs hiển thị đầy đủ endpoints (dù placeholder)
✅ make test pass
✅ Code theo Clean Architecture: main.py → api/ → services/ → repositories/ → models/
```