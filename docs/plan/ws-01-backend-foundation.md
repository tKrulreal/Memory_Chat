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

| Component | Status |
|-----------|--------|
| `src/main.py` skeleton | ✅ Done |
| `src/models/` | ✅ Done (13 tables) |
| `src/repositories/` | ✅ Done |
| `src/services/` | ✅ Done |
| `src/agents/` | ✅ Done |
| Alembic Migrations | ✅ Done |
| Auth (JWT) | ✅ Done |
| Settings + Config | ✅ Done |
| Middleware + Routers | ✅ Done |
| Unit Tests | ✅ Done |

---

## Database Schema (13 Tables)

### Tables

| Table | Description | File |
|-------|-------------|------|
| `users` | User accounts | `src/models/user.py` |
| `contacts` | Contact list per user | `src/models/contact.py` |
| `contact_memories` | AI-generated knowledge | `src/models/contact.py` |
| `conversations` | Chat conversations | `src/models/chat.py` |
| `conversation_pairs` | Multi-user sync | `src/models/chat.py` |
| `messages` | Chat messages | `src/models/chat.py` |
| `tags` | Contact tags | `src/models/contact.py` |
| `contact_tags` | Tag assignment (N:N) | `src/models/contact.py` |
| `recommendations` | AI suggestions | `src/models/ai.py` |
| `event_logs` | Activity tracking | `src/models/ai.py` |
| `search_history` | Search queries | `src/models/ai.py` |
| `notifications` | User notifications | `src/models/ai.py` |
| `settings` | User preferences | `src/models/ai.py` |

### Migrations

```
alembic/versions/
├── 6bcc6defa0aa_init_schema.py          # Base schema (tags, users, contacts, notifications, etc.)
├── 20260820_001_add_friends_feature.py   # Friends system
├── 20260820_002_add_sender_id_to_messages.py  # sender_id field
├── 20260820_003_add_conversation_pairs.py    # Multi-user sync
└── 40169e3d7c2b_add_insights_to_contact_memories.py  # Insights field
```

---

## TASK-BE-01: Database Models (SQLAlchemy) ✅

**Mô tả:** Định nghĩa 13 bảng schema theo database design.

**Files Created:**

- `src/models/database.py` — Base class, engine, session
- `src/models/user.py` — User model
- `src/models/contact.py` — Contact, Tag, ContactMemory, contact_tag_table
- `src/models/chat.py` — Conversation, ConversationPair, Message
- `src/models/ai.py` — Recommendation, EventLog, SearchHistory, Notification, Setting
- `src/models/schemas.py` — SQLAlchemy model configs
- `src/models/__init__.py` — Model exports

**Models Structure:**

```python
# User - has many Contacts, Conversations, Settings
class User(Base):
    __tablename__ = "users"
    id: uuid_pk
    email: str (unique)
    password_hash: str
    full_name: str
    avatar: str | None
    created_at, updated_at

# Contact - belongs to User, has Memory, Conversations, Tags
class Contact(Base):
    __tablename__ = "contacts"
    id: uuid_pk
    user_id: FK(users.id)
    display_name, avatar, phone, email
    created_at, updated_at

# ContactMemory - 1:1 with Contact
class ContactMemory(Base):
    __tablename__ = "contact_memories"
    id: uuid_pk
    contact_id: FK(contacts.id, unique)
    summary, profession, company
    skills, interest, timeline (JSON)
    relationship_score, last_discussion, insights (JSON)
    updated_at

# Conversation - belongs to User + Contact, has Messages
class Conversation(Base):
    __tablename__ = "conversations"
    id: uuid_pk
    user_id: FK(users.id)
    contact_id: FK(contacts.id)
    conversation_pair_id: FK(conversation_pairs.id, nullable)
    title, last_message, last_message_time, status
    created_at, updated_at

# ConversationPair - links 2 conversations for multi-user sync
class ConversationPair(Base):
    __tablename__ = "conversation_pairs"
    id: uuid_pk
    user_1_id, user_2_id: FK(users.id)

# Message - belongs to Conversation
class Message(Base):
    __tablename__ = "messages"
    id: uuid_pk
    conversation_id: FK(conversations.id)
    sender_id: FK(users.id, nullable)
    sender_type: str (USER/CONTACT)
    content, message_type (TEXT/AI/SYSTEM)
    created_at

# Tag + ContactTag (N:N)
class Tag(Base):
    __tablename__ = "tags"
    id: uuid_pk
    name: str (unique)
    color, created_at

contact_tag_table = Table("contact_tags", ...)
```

---

## TASK-BE-02: Alembic Migration ✅

**Mô tả:** Khởi tạo Alembic và tạo migrations cho toàn bộ schema.

**Commands:**

```bash
alembic init alembic
alembic revision --autogenerate -m "init schema"
alembic upgrade head
```

**Verify:**

```bash
sqlite3 data/app.db ".tables"
# Output: contacts contact_memories contact_tags conversations conversation_pairs event_logs messages notifications recommendations search_history settings tags users
```

---

## TASK-BE-03: Repositories (CRUD layer) ✅

**Mô tả:** Implement Repository pattern cho mỗi model.

**Files Created:**

- `src/repositories/base.py` — BaseRepository generic
- `src/repositories/user_repo.py`
- `src/repositories/contact_repo.py`
- `src/repositories/conversation_repo.py`
- `src/repositories/message_repo.py`
- `src/repositories/memory_repo.py`
- `src/repositories/recommendation_repo.py`
- `src/repositories/event_log_repo.py`
- `src/repositories/search_history_repo.py`
- `src/repositories/notification_repo.py`
- `src/repositories/setting_repo.py`
- `src/repositories/tag_repo.py`

---

## TASK-BE-04: Services (business logic) ✅

**Mô tả:** Service layer gọi Repository + áp dụng business rules.

**Files Created:**

- `src/services/auth.py` — register, login, verify_token
- `src/services/contact.py` — CRUD + logic
- `src/services/conversation.py` — CRUD + pair logic
- `src/services/message.py` — CRUD + emit event
- `src/services/memory.py` — CRUD + trigger agent
- `src/services/recommendation.py` — CRUD + accept/reject
- `src/services/event_log.py` — event logging
- `src/services/friends.py` — friend request system
- `src/services/llm.py` — LLM Gateway
- `src/services/vector_store.py` — ChromaDB wrapper

---

## TASK-BE-05: LLM Gateway (retry + log) ✅

**Mô tả:** Unified interface cho LLM providers.

**Features:**

- Support multiple providers: OpenAI, OpenRouter, Anthropic
- Configurable via `.env`: `OPENAI_API_KEY`, `OPENROUTER_API_KEY`
- Model config: `LLM_MODEL=gpt-4o` (default)
- Retry with exponential backoff (max 3 retries)
- Token usage logging
- Prompt/response logging to `.ai-log/`
- Timeout config: `LLM_TIMEOUT=30`

**API:**

```python
class LLMGateway:
    async def chat(messages: list[dict]) -> str
    async def complete(prompt: str, **kwargs) -> str
    async def embed(texts: list[str]) -> list[list[float]]
```

---

## TASK-BE-06: Auth (JWT + bcrypt) ✅

**Mô tả:** AuthService + middleware xác thực JWT.

**Features:**

- Register: email, password, full_name
- Login: email + password → JWT access_token
- Token refresh (optional)
- Logout (optional)
- Password hashing: bcrypt
- JWT secret: from env `JWT_SECRET`
- Token expire: `JWT_EXPIRE_MINUTES=60`

**Endpoints:**

```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh (optional)
POST /api/v1/auth/logout (optional)
GET  /api/v1/auth/me
```

---

## TASK-BE-07: Settings + Config ✅

**Mô tả:** Pydantic Settings từ environment.

**Config:**

```python
# src/config.py
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./data/app.db"
    
    # LLM
    OPENAI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_TIMEOUT: int = 30
    
    # JWT
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./.ai-log"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"
```

---

## TASK-BE-08: Middleware + Routers ✅

**Mô tả:** Kết nối các thành phần vào main.py.

**Routers Created:**

```
src/api/v1/
├── router.py         # Main router (include all)
├── auth.py          # /auth/*
├── contacts.py      # /contacts/*
├── conversations.py  # /conversations/*
├── messages.py      # /messages/*
├── friends.py       # /friends/*
├── memory.py        # /memory/*
├── search.py        # /search/*
├── recommendations.py # /recommendations/*
├── copilot.py       # /copilot/*
├── settings.py      # /settings/*
├── notifications.py # /notifications/*
├── events.py        # /events/*
└── connections.py   # /connections/*
```

**Middleware:**

- CORS middleware (configurable origins)
- Request logging (JSON format)
- Request ID tracking (UUID)
- Global exception handler
- JWT authentication (get_current_user dependency)

---

## TASK-BE-09: Unit tests cho Repository + Service ✅

**Mô tả:** Test cho Repository + Service layer.

**Coverage:**

```
tests/
├── conftest.py          # Fixtures (DB, client, user)
├── unit/
│   ├── repositories/    # Repository tests
│   ├── services/        # Service tests
│   └── test_llm_gateway.py
└── test_auth.py
```

---

## TASK-BE-10: Unit test Auth ✅

**Mô tả:** Test cho AuthService + API endpoints.

**Coverage:**

- register: success + duplicate email
- login: success + wrong password
- verify_token: valid + expired + invalid
- API endpoints: 200 + 401

---

## TASK-BE-11: Cập nhật `.env.example` ✅

**Mô tả:** Environment variables đầy đủ.

```bash
# Database
DATABASE_URL=sqlite:///./data/app.db

# LLM - OpenAI
OPENAI_API_KEY=sk-...

# LLM - OpenRouter (alternative)
OPENROUTER_API_KEY=sk-or-...

# Model
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
LLM_TIMEOUT=30

# JWT
JWT_SECRET=change-me-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma

# Logging
LOG_LEVEL=INFO
LOG_DIR=./.ai-log

# CORS
CORS_ORIGINS=http://localhost:5173
```

---

## TASK-BE-12: Cập nhật README ✅

**Mô tả:** Cập nhật README.md chính.

**Sections:**

- Quick Start
- Architecture
- Tech Stack
- Environment Variables
- Database Migration
- Running Tests
- Project Structure

---

## Kết quả mong đợi sau WS-01

```
✅ 13 bảng DB đã migrate thành công
✅ Alembic upgrade head chạy trên SQLite trống
✅ Repository + Service layer đầy đủ + có unit test
✅ LLM Gateway có retry + log
✅ Auth register + login trả JWT hợp lệ
✅ Tất cả router được include trong main.py
✅ Swagger UI tại /docs hiển thị đầy đủ endpoints
✅ make test pass
✅ Code theo Clean Architecture
```

---

## Trạng thái hoàn thành

| Task | Status | Evidence |
|------|--------|----------|
| TASK-BE-01: Database Models | ✅ Done | `src/models/*.py` |
| TASK-BE-02: Alembic Migration | ✅ Done | `alembic/versions/*.py` |
| TASK-BE-03: Repositories | ✅ Done | `src/repositories/*.py` |
| TASK-BE-04: Services | ✅ Done | `src/services/*.py` |
| TASK-BE-05: LLM Gateway | ✅ Done | `src/services/llm.py` |
| TASK-BE-06: Auth | ✅ Done | `src/services/auth.py`, `src/api/v1/auth.py` |
| TASK-BE-07: Settings | ✅ Done | `src/config.py` |
| TASK-BE-08: Middleware + Routers | ✅ Done | `src/api/v1/router.py` |
| TASK-BE-09: Unit tests Repository | ✅ Done | `tests/unit/repositories/` |
| TASK-BE-10: Unit test Auth | ✅ Done | `tests/test_auth.py` |
| TASK-BE-11: .env.example | ✅ Done | `.env.example` |
| TASK-BE-12: README | ✅ Done | `README.md` |

---

*Version: 2.0 (Specv2 aligned)*
*Last Updated: 2026-08-14*
