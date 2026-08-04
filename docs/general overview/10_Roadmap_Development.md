# 10_Roadmap_Development.md

# Development Roadmap

Project: MemoryChat

Duration: 6 Weeks

Version: MVP v1.0

---

# 1. Overview

MemoryChat được phát triển trong thời gian 6 tuần.

Do thời gian hạn chế, nhóm lựa chọn chiến lược: **Build Small, Validate Fast.**

Mục tiêu không phải xây dựng một ứng dụng chat hoàn chỉnh như Messenger hay Zalo.

Thay vào đó, nhóm tập trung chứng minh giá trị cốt lõi:

> AI có thể giúp người dùng ghi nhớ, quản lý và khai thác các mối quan hệ thông qua dữ liệu hội thoại.

Toàn bộ kế hoạch phát triển được chia thành các Sprint theo tuần với từng mốc kiểm thử rõ ràng.

> **Trạng thái MVP hiện tại**: Codebase đã có một FastAPI skeleton với LangGraph `StateGraph` cơ bản (`analyze` → `respond`), kết nối OpenAI qua LangChain, lưu trữ SQLite + ChromaDB. Các sprint dưới đây mở rộng skeleton này thành MemoryChat hoàn chỉnh.

---

# 2. Development Strategy

Nhóm ưu tiên theo thức tự sau:

```
Core Chat
  ↓
Data Collection
  ↓
AI Memory
  ↓
Search
  ↓
Recommendation
  ↓
AI Copilot
  ↓
Frontend
```

Nếu Chat chưa ổn định, AI sẽ không có dữ liệu để hoạt động. Do đó Chat luôn là nền tảng.

---

# 3. Tech Stack MVP (đã có)

| Layer | Tech |
|-------|------|
| API Framework | FastAPI + Uvicorn |
| LLM | OpenAI `gpt-4o-mini` qua LangChain |
| Agent Orchestration | LangGraph |
| Database | SQLite (SQLAlchemy) |
| Vector DB | ChromaDB (persistent local) |
| Validation | Pydantic v2 |
| Container | Docker (single service) |
| Dev Tools | Makefile, `.env.example` |

---

# 4. Team Structure

| Member | Vai trò |
|--------|---------|
| Member 1 | Project Lead, AI Architecture, Backend, LLM Integration |
| Member 2 | Frontend (React/Flutter), UI/UX, VinUni Red Design System |
| Member 3 | Backend, Database (SQLite → PostgreSQL), Auth, Realtime Chat |
| Member 4 | AI Engineer, Embedding, Vector DB, Recommendation |

---

# 5. Sprint Overview

| Sprint | Mục tiêu |
|--------|----------|
| Week 1 | Foundation & Backend Skeleton |
| Week 2 | Chat System |
| Week 3 | AI Memory |
| Week 4 | Search + Recommendation |
| Week 5 | AI Copilot + Frontend |
| Week 6 | Testing + Demo |

---

# 6. Week 1 — Foundation & Backend Skeleton

## Goal

Hoàn thành nền tảng dự án. ✅ Đã có skeleton từ AI20K template.

## Backend

- ✅ Khởi tạo FastAPI (`src/main.py`).
- ✅ Cấu hình Settings (`src/config.py`).
- ✅ Kết nối OpenAI qua LangChain (`src/services/llm.py`).
- ✅ LangGraph skeleton (`src/agents/graph.py`).
- ✅ Docker Compose single service.
- ⬜ Migration sang Alembic + SQLAlchemy ORM.
- ⬜ Tạo schema (User, Contact, Conversation, Message, ContactMemory, Recommendation, EventLog).

## Frontend

- Thiết kế Design System (VinUni Red).
- Khởi tạo React project (TypeScript + Vite + TailwindCSS).

## AI

- ⬜ Tách `src/agents/graph.py` thành Assistant Orchestrator.
- ⬜ Context Builder + Prompt Builder.
- ⬜ Tool Registry skeleton.

## Deliverables

- Project chạy được bằng `make run`.
- Swagger UI tại `/docs`.
- Skeleton Database schema.

---

# 7. Week 2 — Chat System

## Goal

Hoàn thiện Chat và Event Bus.

## Backend

- Conversation API.
- Message API.
- Contact API.
- WebSocket (sau MVP có thể dùng polling).
- Event ghi vào `EventLog` (SQLite).
- Asyncio background task xử lý event.

## Frontend

- Conversation List.
- Chat Screen.
- Input Box.
- Send Message.
- Mock Contact (do chưa có multi-user).

## AI

- Trigger Memory Refresh khi conversation idle.
- Trigger Embedding Update.

## Deliverables

- Chat hoạt động.
- Event được ghi nhận.
- Background task chạy được.

---

# 8. Week 3 — AI Memory

## Goal

Memory System hoạt động end-to-end.

## Backend

- ContactMemory API.
- Memory Worker (asyncio).
- Embedding Update worker.

## AI

- Memory Agent: Summary + Entity Extraction.
- Embedding Generation (OpenAI Embeddings).
- ChromaDB upsert (`contact_memory_embedding`).
- Relationship Score calculation.

## Frontend

- Context Card.
- Contact Profile.

## Deliverables

- AI tạo Contact Memory từ conversation.
- Hiển thị Summary.
- Timeline hoạt động.
- Embedding được lưu ChromaDB.

---

# 9. Week 4 — Search + Recommendation

## Goal

Semantic Search và Recommendation.

## Backend

- Search API.
- Recommendation API.

## AI

- Search Agent (ChromaDB + LLM Re-ranking).
- Recommendation Agent.
- Insight Agent.

## Frontend

- Search Screen.
- Recommendation Center.

## Deliverables

- Semantic Search trả kết quả đúng.
- Follow-up Recommendation.
- Connection Recommendation.

---

# 10. Week 5 — AI Copilot + Frontend Polish

## Goal

AI Copilot hoàn chỉnh + Frontend MVP.

## Backend

- Copilot API.
- Tool Registry hoàn chỉnh.
- Context Builder.
- Response Validator.

## AI

- Assistant Orchestrator (LangGraph đầy đủ).
- Intent Detection Node.
- Tool Calling Node.
- Tagging Agent.
- Connection Agent.

## Frontend

- AI Button.
- Bottom Sheet.
- Share to Conversation.
- Notification Center.

## Deliverables

- Copilot trả lời theo ngữ cảnh.
- Có thể chia sẻ gợi ý vào ô nhập tin nhắn.
- Frontend MVP chạy được.

---

# 11. Week 6 — Testing & Demo

## Goal

Hoàn thiện MVP.

## Công việc

- Bug Fix.
- UI Polish.
- AI Prompt Tuning.
- Test (Unit + Integration + Manual).
- Demo Script.
- Slide.
- Video.

## Deliverables

- MVP ổn định.
- Demo hoàn chỉnh.
- Tài liệu đầy đủ (`docs/general overview/` + `docs/plan/`).

---

# 12. Task Priority

## P0 — Must Have

- Authentication (JWT).
- Chat (Conversation + Message).
- Contact.
- Memory.
- Search.
- Recommendation.
- AI Copilot.
- Frontend (React/Flutter).

## P1 — Should Have

- Connection Recommendation.
- Context Card.
- Timeline.
- Contact Insight.
- Tagging Agent.

## P2 — Nice to Have

- Merge Contact.
- Advanced Analytics.
- Notification Center.
- Multi-LLM Provider.
- Prompt Versioning.

---

# 13. Definition of Done

Một tính năng được xem là hoàn thành khi:

- Code Review hoàn tất.
- Unit Test đạt yêu cầu.
- API hoạt động ổn định.
- Frontend tích hợp thành công.
- Không có lỗi nghiêm trọng.
- Có thể demo.
- Có tài liệu mô tả.

---

# 14. Testing Strategy

## Backend

- Unit Test (`pytest`).
- API Test (FastAPI TestClient).

## Frontend

- UI Test.
- Manual Test.

## AI

- Prompt Testing.
- Memory Accuracy.
- Search Accuracy.
- Recommendation Quality.

## End-to-End

- Login.
- Chat.
- Memory Update.
- Search.
- Recommendation.
- Copilot.
- Share to Conversation.

---

# 15. Success Metrics

## Technical

- API < 300ms.
- Search < 2 giây.
- Memory Update < 10 giây.
- Recommendation Generation < 5 giây.

## AI

- Summary Acceptance > 80%.
- Search Precision > 85%.
- Recommendation CTR > 60%.

## Product

- Context Retrieval < 30 giây.
- CSAT > 4/5.
- Người dùng hoàn thành demo mà không cần hướng dẫn.

---

# 16. Risks & Mitigation

## LLM Latency

**Giải pháp**: Async Worker (asyncio trong MVP), Cache, Retry.

## API Cost

**Giải pháp**: Batch Processing, Prompt Compression, Embedding Incremental, dùng `gpt-4o-mini`.

## Recommendation chưa chính xác

**Giải pháp**: Rule-based Filter, Human-in-the-loop, Feedback Loop.

## Scope quá lớn

**Giải pháp**: Ưu tiên P0, loại bỏ các tính năng không ảnh hưởng giá trị cốt lõi.

## MVP đơn giản (single container) không scale

**Giải pháp**: Thiết kế DB-agnostic, Event-driven. Khi scale, chuyển SQLite → PostgreSQL, ChromaDB → Qdrant, thêm Celery + Redis mà không đổi Business Logic.

---

# 17. Future Roadmap

Sau MVP có thể phát triển:

### Phase 2

- Group Chat.
- Calendar Integration.
- Gmail Integration.
- Voice Note Summary.
- Meeting Summary.
- SQLite → PostgreSQL migration.

### Phase 3

- MCP Server.
- Multi-Agent Collaboration.
- Local LLM.
- Cross-platform Sync.
- CRM Integration.
- ChromaDB → Qdrant + Neo4j.

### Phase 4

- AI Personal CRM.
- Smart Networking.
- Team Workspace.
- Enterprise Edition.
- Kubernetes deployment.

---

# 18. Final Deliverables

Kết thúc dự án, nhóm sẽ bàn giao:

- Source Code (Backend + Frontend).
- AI Services.
- Docker Compose.
- Database Schema.
- API Documentation (Swagger `/docs`).
- PRD, Architecture Document.
- Wireframe.
- Demo Video.
- Slide Pitching.
- User Manual.

---

# 19. Project Principles

- Chat chỉ là phương tiện tạo dữ liệu.
- AI mới là giá trị cốt lõi.
- Human-in-the-loop cho mọi quyết định quan trọng.
- Mọi AI đều dựa trên ngữ cảnh.
- Thiết kế hướng mở rộng nhưng triển khai vừa đủ cho MVP.
- Ưu tiên hoàn thành một sản phẩm chạy tốt hơn là xây quá nhiều tính năng chưa hoàn thiệt.
- DB-agnostic: code không phụ thuộc SQLite hay PostgreSQL, ChromaDB hay Qdrant.