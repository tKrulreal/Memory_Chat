# WS-03 — AI Memory

> **Mục tiêu:** Biến hội thoại thành tri thức — Memory Agent tạo ContactMemory, Embedding Agent upsert ChromaDB.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | WS-03 (sau WS-02) |
| Độ phức tạp | 🔴 Cao |
| Phụ thuộc | WS-01 (Backend Foundation), WS-02 (Chat System) |
| Unblock | WS-04, WS-05, WS-06 |

> **Specification Reference:** Xem chi tiết tại [AI Agents Architecture - Memory Agent](../specs/ai-agents.md#4-memory-agent)

---

## Trạng thái hiện tại

- ✅ `src/agents/graph.py` skeleton (LangGraph `analyze` + `respond`).
- ✅ `src/services/llm.py` (LLM Gateway) - đã tích hợp Embedding Service.
- ✅ `src/agents/memory/agent.py` - Memory Agent hoàn chỉnh.
- ✅ `src/services/vector_store.py` - ChromaDB wrapper.
- ✅ `src/workers/memory_worker.py` - Background worker subscribe EventBus.
- ✅ `src/api/v1/memory.py` - Memory API endpoints.

---

## TASK-MEM-01: Embedding Service (OpenAI Embeddings) ✅

**Mô tả:** Wrapper cho OpenAI Embeddings API — chuyển text thành vector.

> **Note:** Embedding được tích hợp trong `src/services/llm.py` (LLMGateway.embed())

**Checklist:**
- [x] `LLMGateway.embed(text)` method trong `src/services/llm.py`
- [x] Dùng `text-embedding-3-small` model (1536 dim)
- [x] Retry với exponential backoff (tenacity)
- [x] Log prompt + embedding vào `.ai-log/`
- [x] Configurable qua `settings.embedding_model`

**Commands:**
```bash
# Test Embedding
python -c "
from src.services.llm import LLMGateway
g = LLMGateway()
v = g.embed('Xin chào')
print(len(v))  # 1536
"
```

---

## TASK-MEM-02: Vector Store Service (ChromaDB) ✅

**Mô tả:** Wrapper cho ChromaDB — quản lý collection `contact_memory_embedding`.

> **Reference:** Xem chi tiết tại [Database Schema - Vector Database](../specs/database.md#5-vector-database-chromadb)

**Checklist:**
- [x] `src/services/vector_store.py` (VectorStoreService class)
- [x] Persistent client: `./data/chroma` (config từ env: `CHROMA_PERSIST_DIR`)
- [x] Collection: `contact_memory_embedding`
- [x] Method `upsert(memory_id, text, embedding, metadata)`
- [x] Method `query(query_embedding, top_k=10) -> list[dict]`
- [x] Method `delete(memory_id)`
- [x] Method `count() -> int`
- [x] Metadata schema: `{ contact_id, user_id, memory_id, updated_at }`
- [x] Singleton pattern cho reuse

**Commands:**
```bash
# Test Vector Store
python -c "
from src.services.vector_store import VectorStoreService
vs = VectorStoreService.get_instance()
vs.upsert('mem-1', 'Người này thích lập trình', [0.1]*1536, {'contact_id': '1'})
print(vs.count())
print(vs.query([0.1]*1536, top_k=5))
"
```

---

## TASK-MEM-03: Memory Agent (summary + entity extraction) ✅

**Mô tả:** Memory Agent — phân tích conversation và sinh ContactMemory.

**Checklist:**
- [x] `src/agents/memory/agent.py` - MemoryAgent class
- [x] Prompt Templates cho Memory (summary + entities)
- [x] Chunking utility (token-aware, ~500 token/chunk)
- [x] Method `summarize(messages) -> str`
- [x] Method `extract_entities(messages) -> dict` (company, profession, skills, interests)
- [x] Method `calculate_relationship_score(messages) -> int` (rule-based)
- [x] Method `build_memory(contact_id, messages) -> MemoryResult`
- [x] Dùng LLM Gateway (`gpt-4o-mini`)
- [x] Method `build_timeline(messages) -> list[dict]`

**Commands:**
```bash
# Test Memory Agent
python -c "
from src.agents.memory import MemoryAgent
agent = MemoryAgent()
# Sync test
print('MemoryAgent initialized')
"
```

---

## TASK-MEM-04: Memory Worker (subscribe EventBus) ✅

**Mô tả:** Background worker subscribe `EventBus` → trigger Memory Refresh theo event.

**Trigger logic:**
- `SEND_MESSAGE` → check: nếu conversation idle > 5 phút → trigger refresh
- `CLOSE_CHAT` → trigger refresh ngay
- `OPEN_AI` (manual button) → trigger refresh ngay

**Checklist:**
- [x] `src/workers/memory_worker.py` - MemoryWorker class
- [x] Subscribe EventBus event `SEND_MESSAGE`, `CLOSE_CHAT`, `OPEN_AI`
- [x] Check `last_message_time` của conversation — nếu idle > 5 phút → trigger
- [x] Call Memory Agent → save ContactMemory + upsert ChromaDB
- [x] Không block event loop (chạy async task)
- [x] Handle LLM error gracefully (log + retry 1 lần)
- [x] Worker khởi động trong lifespan (main.py)
- [x] Log mỗi lần refresh

**Commands:**
```bash
# Test Worker - verify in main.py lifespan
# MemoryWorker được khởi tạo và subscribe trong app startup
```

---

## TASK-MEM-05: Memory API (CRUD + refresh) ✅

**Mô tả:** REST API cho Memory — lấy, refresh, edit.

**Endpoints:**

```
GET    /api/v1/memory/{contact_id}               — Lấy Memory hiện tại của Contact
POST   /api/v1/memory/{contact_id}/refresh       — Trigger Memory Refresh ngay
PATCH  /api/v1/memory/{contact_id}               — User edit Memory (summary, tags...)
GET    /api/v1/memory/{contact_id}/timeline      — Lấy timeline (sự kiện theo thời gian)
```

**Checklist:**
- [x] `src/api/v1/memory.py` router
- [x] Inject `MemoryService` qua Depends
- [x] Apply `get_current_user` (auth)
- [x] `GET /memory/{id}` — trả ContactMemory JSON đầy đủ
- [x] `POST /memory/{id}/refresh` — emit Event `OPEN_AI` → Worker xử lý
- [x] `PATCH /memory/{id}` — update summary + tags (user edit)
- [x] `GET /memory/{id}/timeline` — query Messages group by date
- [x] Response shape đầy đủ

**Commands:**
```bash
# Test Memory API
curl http://localhost:8000/api/v1/memory/1 \
  -H "Authorization: Bearer $TOKEN"

curl -X POST http://localhost:8000/api/v1/memory/1/refresh \
  -H "Authorization: Bearer $TOKEN"
```

---

## Kết quả mong đợi sau WS-03

```
✅ Conversation mới → sau 5 phút idle → ContactMemory tự động sinh
✅ ChromaDB có embeddings cho mỗi Memory (./data/chroma)
✅ API trả Memory đúng format
✅ User có thể edit Memory qua PATCH
✅ Embedding tồn tại trong ChromaDB collection contact_memory_embedding
✅ Context Recall (mở chat) trả về Memory của Contact đó
✅ Test E2E Memory flow pass
```

---

## Trạng thái hoàn thành

| Task | Status | Evidence |
|------|--------|----------|
| TASK-MEM-01: Embedding Service | ✅ Done | `src/services/llm.py` - `LLMGateway.embed()` |
| TASK-MEM-02: Vector Store (ChromaDB) | ✅ Done | `src/services/vector_store.py` |
| TASK-MEM-03: Memory Agent | ✅ Done | `src/agents/memory/agent.py` |
| TASK-MEM-04: Memory Worker | ✅ Done | `src/workers/memory_worker.py` |
| TASK-MEM-05: Memory API | ✅ Done | `src/api/v1/memory.py` |