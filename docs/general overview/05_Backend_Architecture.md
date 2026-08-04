# 05_Backend_Architecture.md

# Backend Architecture

Project: MemoryChat

Version: MVP v1.0

---

# 1. Overview

Backend của MemoryChat được thiết kế theo hướng **AI-native, Event-driven và Modular Monolith**.

Khác với các ứng dụng CRUD truyền thống, phần lớn giá trị của hệ thống đến từ các AI Workflow. Vì vậy backend không chỉ xử lý API mà còn đóng vai trí điều phối dữ liệu giữa tầng ứng dụng, AI Agents và các hệ thống lưu trữ.

Kiến trúc MVP đáp ứng các yêu cầu:

- Dễ mở rộng khi số lượng AI Agent tăng lên.
- Tách biệt Business Logic và AI Logic.
- Có thể thay đổi LLM hoặc Vector Database trong tương lai.
- Không để AI làm ảnh hưởng đến trải nghiệm người dùng.

Trong giai đoạn MVP, để tối ưu cho hackathon 6 tuần và demo, hệ thống chạy **single-process FastAPI** với LangGraph Agent trong cùng một container. Event Bus, Cache, Background Worker được đơn giản hoá thành in-memory scheduler. Các thành phần này sẽ được tách ra khi scale (xem [08_Deployment_&_Infrastructure.md](08_Deployment_&_Infrastructure.md)).

---

# 2. High-Level Architecture

```
                         Client
                            │
                  REST API (FastAPI)
                            │
              ┌─────────────┴─────────────┐
              │                           │
     Application Services          AI Service Layer
              │                           │
     Repository Layer        LangGraph Orchestrator
              │                           │
       SQLite (PostgreSQL      LLM Gateway (OpenAI)
         sau MVP)                      │
              │                  ChromaDB (Qdrant
              │                    sau MVP)
              └─────────────┬─────────────┘
                            │
                  In-process Event Loop (MVP)
                            │
                  Background Tasks (asyncio)
```

---

# 3. Technology Stack — MVP

| Layer | Technology | Trạng thái |
|--------|------------|------------|
| API Framework | FastAPI | ✅ MVP |
| ASGI Server | Uvicorn | ✅ MVP |
| Validation | Pydantic v2 | ✅ MVP |
| Settings | Pydantic Settings | ✅ MVP |
| LLM Framework | LangGraph + LangChain | ✅ MVP |
| LLM Provider | OpenAI (`gpt-4o-mini`) | ✅ MVP |
| Database | SQLite (qua SQLAlchemy) | ✅ MVP |
| Vector Database | ChromaDB | ✅ MVP |
| Container | Docker (single service) | ✅ MVP |
| Background Job | In-process asyncio Task | ✅ MVP |
| Authentication | JWT | ⬜ Sau MVP |
| Message Broker | Redis / Celery | ⬜ Sau MVP |
| Database | PostgreSQL | ⬜ Sau MVP |
| Vector Database | Qdrant | ⬜ Sau MVP |
| Graph DB | Neo4j | ⬜ Sau MVP |

Lý do chọn stack trên cho MVP:

- **FastAPI + Uvicorn**: Async tốt, tài liệu Swagger tự động, dễ tích hợp AI.
- **LangGraph**: Phù hợp cho Multi-Agent orchestration, hỗ trợ state, branching, human-in-the-loop.
- **OpenAI `gpt-4o-mini`**: Chi phí thấp, đủ tốt cho Memory/Search/Recommendation, thay đổi provider chỉ qua LLM Gateway.
- **SQLite**: Không cần thêm service, dễ dev/demo.
- **ChromaDB**: Vector DB nhẹ, chạy local, persist ra filesystem.
- **Docker single service**: Triển khai 1 lệnh, phù hợp demo.

---

# 4. Folder Structure (MVP)

Cấu trúc hiện tại của codebase MVP:

```
memorychat/
├── src/
│   ├── main.py              # FastAPI entrypoint
│   ├── config.py            # Settings (Pydantic)
│   ├── api/
│   │   └── routes.py        # POST /chat, GET /status
│   ├── agents/
│   │   ├── graph.py         # LangGraph StateGraph
│   │   └── state.py         # AgentState TypedDict
│   ├── services/
│   │   └── llm.py           # ChatOpenAI wrapper
│   ├── models/
│   │   └── schemas.py       # Pydantic request/response
│   └── core/                # Business logic (sẽ mở rộng)
├── tests/
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── .env.example
```

Trong tương lai sẽ mở rộng thành:

```
src/
├── api/             # Presentation Layer
├── core/            # Domain Layer
├── services/        # Application Layer
├── repositories/    # Repository Layer
├── agents/          # AI Agent Layer
│   ├── memory/
│   ├── search/
│   ├── recommendation/
│   ├── tagging/
│   └── connection/
├── workflows/       # LangGraph workflows
├── tools/           # Tool Registry
├── events/          # Event Bus
└── tasks/           # Background Tasks
```

---

# 5. Clean Architecture (hướng đến)

Backend được chia thành các tầng rõ ràng:

```
Client
  ↓
Presentation Layer (FastAPI routes)
  ↓
Application Layer (Services)
  ↓
Domain Layer (Entities, Use Cases)
  ↓
Infrastructure Layer (Repository, LLM, Vector DB)
  ↓
Database / External Services
```

Trong MVP, mọi tầng đều nằm trong `src/` để đơn giản. Việc tách folder sẽ thực hiện khi mở rộng Agent.

---

# 6. Presentation Layer

Chỉ nhận Request, không chứa Business Logic.

Ví dụ MVP hiện tại:

```
POST /api/v1/chat   →  gọi LangGraph Agent
GET  /api/v1/status →  health check
```

Sau MVP sẽ có thêm:

```
POST /api/v1/auth/login
POST /api/v1/auth/register
GET  /api/v1/contacts
GET  /api/v1/conversations
POST /api/v1/messages
GET  /api/v1/search
GET  /api/v1/recommendations
POST /api/v1/copilot
GET  /api/v1/memory/{contact_id}
WS   /ws/chat/{conversation_id}
```

---

# 7. Application Services (sau MVP)

Mỗi Service chỉ xử lý một nghiệp vụ:

```
AuthenticationService
ContactService
ConversationService
MessageService
MemoryService
SearchService
RecommendationService
CopilotService
TagService
NotificationService
```

Service không gọi trực tiếp Database, không gọi trực tiếp LLM.

---

# 8. Repository Pattern (sau MVP)

Business Logic không truy cập Database, thông qua Repository:

```
ConversationRepository
MessageRepository
MemoryRepository
RecommendationRepository
SearchRepository
ContactRepository
```

Repository được inject vào Service — dễ Unit Test và dễ đổi từ SQLite sang PostgreSQL.

---

# 9. Event-driven AI

Dù MVP chưa có Redis Stream, **kiến trúc vẫn theo hướng Event-driven**.

Trong MVP:

- Hành động của User sinh Event ghi vào `EventLog` (SQLite).
- Một asyncio background task đọc Event mới và xử lý.

Sau MVP sẽ thay bằng Redis Stream / Kafka.

Các Event chính:

```
SEND_MESSAGE
OPEN_CHAT
OPEN_AI
SEARCH
UPDATE_CONTACT
APPROVE_TAG
REJECT_TAG
DELETE_MESSAGE
SHARE_TO_CONVERSATION
CONTACT_UPDATED
```

---

# 10. Background Tasks

Trong MVP không có Celery. Background task được implement bằng `asyncio.create_task` chạy trong cùng process FastAPI:

- Memory Refresh (khi conversation idle).
- Embedding Update (sau khi Memory thay đổi).
- Recommendation Generation (sau Memory Update).

Khi scale sẽ tách thành Celery Worker riêng với Redis làm Broker.

---

# 11. AI Service Layer

Toàn bộ AI đều đi qua AI Service. Không Controller nào được gọi trực tiếp LLM.

```
API Request
  ↓
AI Service
  ↓
Assistant Orchestrator (LangGraph)
  ↓
AI Agent (Memory / Search / Recommendation / Tagging / Connection / Insight)
  ↓
LLM Gateway
  ↓
OpenAI API
  ↓
Response Validator
  ↓
API Response
```

Trong MVP, `src/agents/graph.py` đã có một LangGraph `StateGraph` với 2 node: `analyze` và `respond`. Đây là skeleton sẽ mở rộng thành các Agent chuyên biệt.

---

# 12. LLM Gateway

LLM Gateway là lớp trung gian duy nhất giữa Agent và OpenAI.

Trách nhiệm:

- Khởi tạo `ChatOpenAI` từ `OPENAI_API_KEY` + `MODEL_NAME`.
- Retry khi lỗi (qua LangChain retry).
- Logging prompt và response.
- Tính token usage (sau MVP).

Provider trong MVP: **OpenAI** (`gpt-4o-mini`).

Các provider khác (Gemini, Claude, local LLM) sẽ được thêm khi có yêu cầu thực tế — chỉ cần đăng ký thêm trong LLM Gateway.

---

# 13. Authentication

MVP hiện tại chưa có Authentication — API mở.

Sau MVP sẽ thêm:

- JWT Access Token.
- JWT Refresh Token.
- Password Hash (BCrypt).
- Role: `USER`, `ADMIN`.

---

# 14. API Design

### MVP hiện tại

```
POST /api/v1/chat
GET  /api/v1/status
GET  /health
```

### Sau MVP

```
REST API
  /api/auth
  /api/chat
  /api/contact
  /api/search
  /api/recommendation
  /api/copilot
  /api/memory
  /api/tag
  /api/event

WebSocket
  /ws/chat
  /ws/notification
  /ws/copilot
```

---

# 15. Security

### MVP

- HTTPS (do reverse proxy đảm nhiệnh).
- Input Validation (Pydantic).

### Sau MVP

- JWT Authentication.
- Password Hash (BCrypt).
- SQL Injection Protection (SQLAlchemy ORM).
- XSS Protection.
- Rate Limiting.
- Audit Log.
- Prompt Injection Detection.
- Sensitive Data Filtering.
- Context Isolation giữa các User.

---

# 16. Scalability

### MVP

- Single FastAPI process.
- Single SQLite file.
- Single ChromaDB persist dir.

### Sau MVP

| Thành phần | Scale theo chiều nào |
|------------|---------------------|
| FastAPI | Horizontal (nhiều instance + Nginx) |
| Worker | Horizontal (Celery + Redis) |
| SQLite → PostgreSQL | Read replica, partitioning |
| ChromaDB → Qdrant | Cluster mode |
| Neo4j | Cluster mode (bổ sung) |
| LLM | Đổi Provider, hoặc Self-host |

Backend không phụ thuộc một LLM cụ thể.

---

# 17. Error Handling

Phân loại lỗi:

- Validation Error.
- Business Error.
- Infrastructure Error.
- AI Error.
- Timeout.
- Retry.
- Circuit Breaker (sau MVP).

Nếu LLM lỗi: Memory Update thất bại nhưng Chat vẫn hoạt động bình thường.

---

# 18. Logging & Monitoring

### MVP

- Application Log (`stdout` của container).
- AI Log (prompt + response, lưu `.ai-log/`).
- Error Log.

### Sau MVP

- Prometheus + Grafana.
- OpenTelemetry tracing.
- Worker Queue Monitoring.

---

# 19. Design Principles

- Backend chỉ xử lý Business Logic.
- AI chạy bất đồng bộ (qua asyncio task / Celery).
- Mọi Agent đều thông qua Orchestrator (LangGraph).
- Event là nguồn kích hoạt AI.
- Không Controller nào gọi trực tiếp LLM.
- Không để AI làm chậm trải nghiệm nhắn tin.
- Có thể thay thế LLM, Embedding Model hoặc Vector Database mà không cần sửa Business Logic.
- Hệ thống được thiết kế theo hướng Microservice-ready nhưng triển khai Monolith trong MVP để giảm độ phức tạp.