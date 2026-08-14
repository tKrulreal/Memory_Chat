# MemoryChat — Project Plan

## Tổng quan dự án

**Dự án:** MemoryChat — AI-native messaging platform có long-term relationship memory.

**Mục tiêu MVP:** Chứng minh rằng hội thoại có thể được AI "nhớ" và "hiểu" để hỗ trợ người dùng nhắn tin hiệu quả hơn (semantic search, recommendation, AI copilot).

**Product Positioning:**

> **AI-native Messaging Platform with Long-term Relationship Memory**

AI được định vị như một "Second Brain" cho người dùng — giúp ghi nhớ và hiểu các mối quan hệ theo thời gian.

**Core Product Loop:**

```
Chat → Data → Memory → Knowledge → Recommendation → Action
```

---

## Tech Stack (MVP)

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Frontend** | React + Vite + TypeScript | Web App |
| **API** | FastAPI + Uvicorn | REST + WebSocket |
| **LLM** | GPT-4o / OpenRouter | Configurable qua .env |
| **Embedding** | OpenAI text-embedding-3-small | 1536 dimensions |
| **Agent Framework** | LangGraph | AI Orchestration |
| **Database** | SQLite | MVP (PostgreSQL future) |
| **Vector DB** | ChromaDB | Local persist `./data/chroma` |
| **Validation** | Pydantic v2 | Request/Response schemas |
| **Cache** | In-Memory | Redis (future) |
| **Container** | Docker | Single service MVP |

**Tech Stack tương lai (sau MVP):** PostgreSQL, Qdrant, Neo4j, Redis/Celery.

---

## Database Schema (12 Tables)

| Table | Purpose |
|-------|---------|
| `users` | User accounts |
| `contacts` | Contact list (per user) |
| `contact_memories` | AI-generated knowledge about contacts |
| `conversations` | Chat conversations |
| `conversation_pairs` | Sync between 2 users |
| `messages` | Chat messages |
| `tags` | Contact tags |
| `contact_tags` | Tag assignment (N:N) |
| `recommendations` | AI suggestions |
| `event_logs` | Activity tracking |
| `search_history` | Search queries |
| `notifications` | User notifications |
| `settings` | User preferences |

---

## AI Architecture

### AI Agents (5 Core)

| Agent | Responsibility |
|-------|---------------|
| **Memory Agent** | Build contact knowledge from conversations |
| **Search Agent** | Semantic search across contacts |
| **Recommendation Agent** | Proactive suggestions (follow-up, reply, connection) |
| **Tagging Agent** | Extract entities and suggest tags |
| **Insight Agent** | Behavioral analysis |

### Orchestrator

```
User Query → Intent Detection → Context Builder → Agent Execution → Response
```

### Memory Architecture

- **Conversation Memory**: Summary, topics, decisions per conversation
- **Contact Memory**: Long-term knowledge (profession, company, skills, interests)
- **Incremental Update**: Only process new messages, merge into existing memory
- **Trigger Conditions**: Idle 5min, 20 new messages, user refresh, nightly sync

---

## Workstreams

| # | Workstream | Tasks | Độ phức tạp | Phụ thuộc |
|---|------------|-------|-------------|-----------|
| 1 | Backend Foundation | 12 | 🟡 Trung bình | — |
| 2 | Chat System | 6 | 🟡 Trung bình | WS-01 |
| 3 | AI Memory | 5 | 🔴 Cao | WS-01 + WS-02 |
| 4 | Search & Recommendation | 7 | 🟡 Trung bình | WS-03 |
| 5 | AI Copilot | 5 | 🔴 Cao | WS-03 + WS-04 |
| 6 | Frontend | 5 | 🟡 Trung bình | WS-02 → WS-05 |
| 7 | DevOps & Deployment | 5 | 🟢 Thấp | — |
| 8 | Testing & Demo | 5 | 🟡 Trung bình | Tất cả WS |

---

## Dependency Map

```
[WS-01: Backend Foundation]
         │
         ▼
[WS-02: Chat System]
         │
         ▼
[WS-03: AI Memory]
         │
         ├──────────────┐
         ▼              ▼
[WS-04: Search]  [WS-05: Copilot]
         │              │
         └──────┬───────┘
                ▼
        [WS-06: Frontend]  ─── chạy song song từ WS-02 → WS-05
                │
                ▼
        [WS-08: Testing & Demo]

[WS-07: DevOps]  ─── chạy song song với tất cả
```

---

## Critical Path

```
WS-01 (Backend Foundation) → WS-02 (Chat) → WS-03 (Memory) → WS-04+05 (Search+Copilot) → WS-08 (Demo)
                    ↓
            WS-06 (Frontend) chạy song song từ WS-02 → WS-05
```

---

## Trạng thái hiện tại

| Component | Trạng thái | Ghi chú |
|-----------|-----------|---------|
| `src/main.py` skeleton | ✅ Có sẵn | FastAPI app |
| `src/models/` | ✅ Hoàn chỉnh | 12 bảng đã migrate |
| `src/agents/` | ✅ Hoàn chỉnh | Memory, Search, Recommendation, Insight |
| `src/api/v1/` | ✅ Hoàn chỉnh | Auth, Chat, Friends, Copilot |
| `src/ws/manager.py` | ✅ Hoàn chỉnh | WebSocket real-time |
| `src/events/bus.py` | ✅ Hoàn chỉnh | Event-driven |
| `frontend/` | ✅ Hoàn chỉnh | React + TS + Tailwind |
| Database Schema | ✅ Done | Alembic migrations |
| Tests | ✅ 158+ tests | Pytest |

---

## Task IDs tổng hợp

**WS-01 — Backend Foundation**
- `TASK-BE-01` Database Models (SQLAlchemy)
- `TASK-BE-02` Alembic Migration
- `TASK-BE-03` Repositories (CRUD layer)
- `TASK-BE-04` Services (business logic)
- `TASK-BE-05` LLM Gateway (retry + log)
- `TASK-BE-06` Auth (JWT + bcrypt)
- `TASK-BE-07` Settings + Config
- `TASK-BE-08` Middleware + Routers
- `TASK-BE-09` Unit tests cho Repository + Service
- `TASK-BE-10` Unit test Auth
- `TASK-BE-11` Cập nhật `.env.example`
- `TASK-BE-12` Cập nhật README

**WS-02 — Chat System**
- `TASK-CHAT-01` Pydantic Schemas (Contact/Conversation/Message)
- `TASK-CHAT-02` Contact API (CRUD)
- `TASK-CHAT-03` Conversation API (CRUD)
- `TASK-CHAT-04` Message API (CRUD)
- `TASK-CHAT-05` WebSocket + Connection Manager
- `TASK-CHAT-06` Event Bus (asyncio + EventLog)

**WS-03 — AI Memory**
- `TASK-MEM-01` Embedding Service (OpenAI Embeddings)
- `TASK-MEM-02` Vector Store Service (ChromaDB)
- `TASK-MEM-03` Memory Agent (summary + entity extraction)
- `TASK-MEM-04` Memory Worker (subscribe EventBus)
- `TASK-MEM-05` Memory API (CRUD + refresh)

**WS-04 — Search & Recommendation**
- `TASK-SR-01` Search Agent (ChromaDB + LLM re-rank)
- `TASK-SR-02` Search API
- `TASK-SR-03` Recommendation Agent (rule-based + LLM)
- `TASK-SR-04` Recommendation API (accept/reject)
- `TASK-SR-05` Insight Agent (behavior analysis)
- `TASK-SR-06` Insight API
- `TASK-SR-07` SearchHistory + Notification

**WS-05 — AI Copilot**
- `TASK-COP-01` Assistant Orchestrator (LangGraph)
- `TASK-COP-02` Tools layer (search, memory, recommendation)
- `TASK-COP-03` Tagging Agent + API
- `TASK-COP-04` Connection Agent + API
- `TASK-COP-05` Copilot API + Share-to-Conversation

**WS-06 — Frontend**
- `TASK-FE-01` Setup (Vite + TS + Tailwind + Router)
- `TASK-FE-02` Design System (tokens + Components)
- `TASK-FE-03` Auth Pages + API integration
- `TASK-FE-04` Chat Pages + WebSocket
- `TASK-FE-05` Search + Recommendation + Copilot Pages

**WS-07 — DevOps & Deployment**
- `TASK-OPS-01` Dockerfile review + multi-stage
- `TASK-OPS-02` Docker Compose + Volume
- `TASK-OPS-03` Makefile targets (run/test/lint/backup)
- `TASK-OPS-04` Scripts (backup.sh + restore.sh + seed.py)
- `TASK-OPS-05` Health check + Structured logging

**WS-08 — Testing & Demo**
- `TASK-TEST-01` Backend tests (Repository + Service + API)
- `TASK-TEST-02` AI tests (Memory + Search + Recommendation + Copilot)
- `TASK-TEST-03` E2E tests (full flow)
- `TASK-TEST-04` Demo Script + Slide + Video
- `TASK-TEST-05` Seed data + User Manual

---

## Product Philosophy

MemoryChat không cố gắng trở thành một phiên bản khác của Messenger hoặc Zalo.

**Giá trị cốt lõi nằm ở AI Layer.**

Hệ thống phải có khả năng biến:

```
Raw Conversation → Structured Information → Memory → Knowledge → Recommendation → User Action
```

**AI chỉ:**
- hiểu, ghi nhớ, phân tích, tìm kiếm, đề xuất

**AI không tự động:**
- gửi tin nhắn, kết bạn, giới thiệu người này với người khác
- merge contact, thực hiện hành động có tác động bên ngoài

**Người dùng luôn giữ quyền quyết định cuối cùng.**

---

## MVP Simplification Rules

Nếu thiếu thời gian, ưu tiên theo thứ tự:

```
1. Chat
2. Memory
3. Context Recall
4. Search
5. Recommendation
6. Copilot
7. Knowledge Graph enhancement
```

Không hy sinh:
- Message persistence
- Authentication
- Data isolation
- Memory correctness

---

## Quick Start

```bash
# Clone and setup
cp .env.example .env
# Edit .env with OPENAI_API_KEY and OPENROUTER_API_KEY

# Run with Docker
docker compose up -d

# Or run locally
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload

# Run tests
pytest tests/ -v

# Frontend
cd frontend
npm install
npm run dev
```

---

*Plan Version: 2.0 (Specv2 aligned)*
*Last Updated: 2026-08-14*
