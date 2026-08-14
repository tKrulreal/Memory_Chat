# Plan Overview & Tracking

> **Mục tiêu:** Bám sát tiến độ 8 Workstream, đảm bảo MVP MemoryChat demo được trong 6 tuần.

**Project:** MemoryChat
**Version:** MVP v2.0 (Specv2 aligned)
**Template nền:** AI20K Agent Template (VinUni AI Thực Chiến)

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | Phase 0 (đầu tiên — setup plan) |
| Độ phức tạp | 🟢 Thấp |
| Phụ thuộc | Không có |
| Unblock | WS-01 → WS-08 |

---

## 1. Mục tiêu tổng quát

MemoryChat = AI-native messaging platform có **long-term relationship memory**.

**Product Positioning:**

> **AI-native Messaging Platform with Long-term Relationship Memory**

AI được định vị như một "Second Brain" cho người dùng.

**Core Product Loop:**

```
Chat → Data → Memory → Knowledge → Recommendation → Action
```

Trong MVP (6 tuần), nhóm cần chứng minh:

1. ✅ Chat hoạt động (REST + WebSocket realtime) — **Real multi-user chat**
2. ✅ AI tự sinh **ContactMemory** từ hội thoại
3. ✅ **Semantic Search** tìm lại Contact theo ngữ nghĩa
4. ✅ **Recommendation** đề xuất Follow-up / Reply / Connection
5. ✅ **AI Copilot** trả lời theo ngữ cảnh người dùng
6. ✅ **Frontend** (React) chạy được end-to-end

---

## 2. Tech Stack

| Layer | MVP | Future |
|-------|-----|--------|
| Frontend | React + Vite + TypeScript | Flutter |
| API | FastAPI | FastAPI |
| LLM | GPT-4o / OpenRouter | Claude/Gemini |
| Embedding | text-embedding-3-small | BGE-M3 |
| Agent | LangGraph | LangGraph |
| Database | SQLite | PostgreSQL |
| Vector DB | ChromaDB | Qdrant |
| Graph DB | — | Neo4j |
| Cache | In-Memory | Redis |

---

## 3. Workstream Map

| ID | Workstream | Status | Owner | Depends On |
|----|------------|--------|-------|------------|
| WS-01 | Backend Foundation | ✅ Done | All | — |
| WS-02 | Chat System | ✅ Done | Member 3 | WS-01 |
| WS-03 | AI Memory | ✅ Done | Member 1 + 4 | WS-01 + WS-02 |
| WS-04 | Search & Recommendation | ✅ Done | Member 4 | WS-03 |
| WS-05 | AI Copilot | ✅ Done | Member 4 | WS-03 + WS-04 |
| WS-06 | Frontend | ✅ Done | Member 2 | WS-02 → WS-05 |
| WS-07 | DevOps & Deployment | ✅ Done | Member 1 | — |
| WS-08 | Testing & Demo | ⬜ Pending | All | All |

**Status key:** ✅ Done | 🟡 In Progress | ⬜ Pending | 🔴 Blocked

---

## 4. Database Schema (13 Tables)

| Table | Purpose | Status |
|-------|---------|--------|
| `users` | User accounts | ✅ |
| `contacts` | Contact list | ✅ |
| `contact_memories` | AI knowledge | ✅ |
| `conversations` | Chat conversations | ✅ |
| `conversation_pairs` | Multi-user sync | ✅ |
| `messages` | Chat messages | ✅ |
| `tags` | Contact tags | ✅ |
| `contact_tags` | N:N relationship | ✅ |
| `recommendations` | AI suggestions | ✅ |
| `event_logs` | Activity tracking | ✅ |
| `search_history` | Search queries | ✅ |
| `notifications` | User notifications | ✅ |
| `settings` | User preferences | ✅ |

---

## 5. AI Architecture

### 5.1 Core Agents

| Agent | Responsibility | Status |
|-------|---------------|--------|
| **Memory Agent** | Build contact knowledge | ✅ |
| **Search Agent** | Semantic search | ✅ |
| **Recommendation Agent** | Proactive suggestions | ✅ |
| **Tagging Agent** | Entity extraction | ✅ |
| **Insight Agent** | Behavior analysis | ✅ |
| **Connection Agent** | Contact matching | ✅ |

### 5.2 Orchestrator

```
User Query → Intent Detection → Context Builder → Agent Execution → Response Validator
```

### 5.3 Memory System

- **Conversation Memory**: Summary, topics, decisions per conversation
- **Contact Memory**: Long-term knowledge (profession, company, skills, interests)
- **Incremental Update**: Only process new messages, merge into existing memory
- **Trigger Conditions**: Idle 5min, 20 new messages, user refresh, nightly sync

---

## 6. Critical Path

```
WS-01 (Backend Foundation)
  ↓
WS-02 (Chat System)
  ↓
WS-03 (AI Memory)
  ↓
WS-04 (Search & Recommendation)
  ↓
WS-05 (AI Copilot)
  ↓
WS-08 (Testing & Demo)

WS-06 (Frontend) ─── chạy song song từ WS-02 đến WS-05
WS-07 (DevOps)      ─── chạy song song với tất cả
```

---

## 7. Deliverables Tracking

| Hạng mục | File | Trạng thái |
|----------|------|------------|
| Spec | `docs/Specv2.md` | ✅ |
| Database Schema | `alembic/versions/` | ✅ |
| Backend API | `src/api/v1/` | ✅ |
| AI Agents | `src/agents/` | ✅ |
| LLM Gateway | `src/services/llm.py` | ✅ |
| Vector Store | `src/services/vector_store.py` | ✅ |
| WebSocket | `src/ws/manager.py` | ✅ |
| Event Bus | `src/events/bus.py` | ✅ |
| Frontend | `frontend/` | ✅ |
| Docker | `docker-compose.yml` | ✅ |
| Tests | `tests/` | ✅ (158+) |

---

## 8. Risk Register

| Risk | Impact | Mitigation |
|------|--------|-----------|
| LLM latency > 5s | Recommendation chậm | Chạy async qua EventBus, không block API |
| API rate limit | Search fail | Retry + exponential backoff |
| Scope quá lớn | Không kịp demo | Ưu tiên P0, cắt P2 (Connection, Insight) |
| ChromaDB corrupt | Mất embedding | Backup volume `./data/` |
| WebSocket proxy | Frontend không kết nối | Sticky session hoặc poll fallback |

---

## 9. Definition of Done (toàn project)

- Tất cả 8 Workstream đạt "Done When"
- E2E test pass: Login → Chat → Memory → Search → Recommendation → Copilot
- Demo chạy trơn tru trong 5 phút, 3 lần liên tiếp không lỗi
- Tài liệu đầy đủ
- Source code tag `v2.0-mvp`

---

## 10. Cập nhật plan

Mỗi khi hoàn thành Task, cập nhật:

- ✅ Check vào Task ID trong file `ws-XX-*.md` (đổi `⬜` thành `[x]` trong checklist)
- ✅ Status Workstream trong bảng §3
- ✅ Status Hạng mục trong bảng §7

---

## Kết quả mong đợi sau Plan Setup

```
✅ Plan folder chuẩn hoá theo template format
✅ 8 Workstream files có task IDs nhất quán
✅ Dependency map rõ ràng
✅ Critical path xác định được
✅ Risk register đầy đủ
✅ Definition of Done thống nhất
✅ Tech Stack đồng nhất với Specv2.md
```

---

*Version: 2.0 (Specv2 aligned)*
*Last Updated: 2026-08-14*
