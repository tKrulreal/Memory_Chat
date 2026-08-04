# MemoryChat — Project Plan

## Tổng quan dự án

**Dự án:** MemoryChat — AI-native messaging platform có long-term relationship memory.

**Mục tiêu MVP:** Chứng minh rằng hội thoại có thể được AI "nhớ" và "hiểu" để hỗ trợ người dùng nhắn tin hiệu quả hơn (semantic search, recommendation, AI copilot).

**Tech Stack MVP:**

| Layer | Technology |
|-------|-----------|
| API | FastAPI + Uvicorn |
| LLM | OpenAI `gpt-4o-mini` (LangChain) |
| Agent | LangGraph |
| Database | SQLite (SQLAlchemy) |
| Vector DB | ChromaDB (local persist) |
| Validation | Pydantic v2 |
| Frontend | React + Vite + TypeScript + TailwindCSS |
| Container | Docker (single service) |
| Dev Tool | Makefile |

**Tech Stack tương lai (sau MVP):** PostgreSQL, Qdrant, Neo4j, Redis, Celery.

**Template nền:** AI20K Agent Template (VinUni AI Thực Chiến starter).

---

## Trạng thái hiện tại

| Component | Trạng thái | Ghi chú |
|-----------|-----------|---------|
| `src/main.py` skeleton | ✅ Có sẵn | Từ AI20K template |
| `src/agents/graph.py` skeleton | ✅ Có sẵn | LangGraph `analyze` + `respond` |
| `src/services/llm.py` skeleton | ✅ Có sẵn | LLM Gateway placeholder |
| `docker-compose.yml` | ✅ Có sẵn | Single service |
| `Makefile` | ✅ Có sẵn | Cần bổ sung target |
| `Dockerfile` | ✅ Có sẵn | Multi-stage build |
| Database Schema | ⬜ Chưa bắt đầu | 11 bảng theo spec |
| Backend API | ⬜ Chưa bắn đầu | REST + WebSocket |
| AI Memory Agent | ⬜ Chưa bắt đầu | |
| Frontend | ⬜ Chưa bắt đầu | React + Vite |
| Demo Video | ⬜ Chưa bắt đầu | |

---

## Workstreams

| # | Workstream | File | Tasks | Độ phức tạp | Phụ thuộc |
|---|------------|------|-------|-------------|-----------|
| 1 | Backend Foundation | [ws-01-backend-foundation.md](./ws-01-backend-foundation.md) | 12 | 🟡 Trung bình | — |
| 2 | Chat System | [ws-02-chat-system.md](./ws-02-chat-system.md) | 6 | 🟡 Trung bình | WS-01 |
| 3 | AI Memory | [ws-03-ai-memory.md](./ws-03-ai-memory.md) | 5 | 🔴 Cao | WS-01 + WS-02 |
| 4 | Search & Recommendation | [ws-04-search-recommendation.md](./ws-04-search-recommendation.md) | 7 | 🟡 Trung bình | WS-03 |
| 5 | AI Copilot | [ws-05-ai-copilot.md](./ws-05-ai-copilot.md) | 5 | 🔴 Cao | WS-03 + WS-04 |
| 6 | Frontend | [ws-06-frontend.md](./ws-06-frontend.md) | 5 | 🟡 Trung bình | WS-02 → WS-05 |
| 7 | DevOps & Deployment | [ws-07-devops-deployment.md](./ws-07-devops-deployment.md) | 5 | 🟢 Thấp | — |
| 8 | Testing & Demo | [ws-08-testing-demo.md](./ws-08-testing-demo.md) | 5 | 🟡 Trung bình | Tất cả WS |

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

**Ghi chú:**
- WS-04 và WS-05 có thể chạy **song song** (cùng phụ thuộc WS-03).
- WS-06 (Frontend) có thể chạy song song với WS-03 → WS-05.
- WS-07 (DevOps) chạy song song với tất cả.
- WS-08 (Testing & Demo) là workstream cuối cùng, phụ thuộc tất cả.

---

## Thứ tự thực hiện đề xuất

```
Ngày 1:
  [Buổi sáng]  WS-01: Models + Repositories + Auth skeleton
  [Buổi chiều] WS-01: LLM Gateway + Alembic migration
  [Buổi tối]   WS-07: Dockerfile + docker-compose (chạy song song)

Ngày 2:
  [Buổi sáng]  WS-02: Contact + Conversation + Message API
  [Buổi chiều] WS-02: WebSocket + Event Bus
  [Buổi tối]   WS-06: Vite + Tailwind + Routing (bắt đầu Frontend)

Ngày 3:
  [Buổi sáng]  WS-03: Embedding service + ChromaDB
  [Buổi chiều] WS-03: Memory Agent + Worker
  [Buổi tối]   WS-06: Design System + Components

Ngày 4:
  [Buổi sáng]  WS-04: Search Agent + Recommendation Agent
  [Buổi chiều] WS-05: Assistant Orchestrator + Copilot API
  [Buổi tối]   WS-06: Pages tích hợp API

Ngày 5:
  [Buổi sáng]  WS-04 + WS-05: Tagging + Connection + Insight
  [Buổi chiều] WS-08: Unit tests + Integration tests
  [Buổi tối]   WS-06: Polish UI + Responsive

Ngày 6 (Demo day):
  [Buổi sáng]  WS-08: E2E tests + Bug fixes
  [Buổi chiều] WS-08: Demo Script + Slide + Video
  [Buổi tối]   Rehearsal demo
```

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
- `TASK-FE-02` Design System (VinUni Red tokens + Components)
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
