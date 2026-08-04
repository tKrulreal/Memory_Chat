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

---

## Trạng thái hiện tại

- ✅ `src/agents/graph.py` skeleton (LangGraph `analyze` + `respond`).
- ✅ `src/services/llm.py` (LLM Gateway).
- ⬜ Memory Agent chưa có.
- ⬜ Embedding service chưa có.
- ⬜ ChromaDB chưa setup.
- ⬜ Memory Worker chưa có.

---

## TASK-MEM-01: Embedding Service (OpenAI Embeddings) ⬜

**Mô tả:** Wrapper cho OpenAI Embeddings API — chuyển text thành vector.

**Checklist:**
- [ ] Tạo `src/services/embedding.py` (EmbeddingService class)
- [ ] Method `embed_text(text: str) -> list[float]`
- [ ] Method `embed_batch(texts: list[str]) -> list[list[float]]`
- [ ] Model: `text-embedding-3-small` (1536 dim)
- [ ] Retry với exponential backoff
- [ ] Cache embedding theo hash(text) để tiết kiệm cost
- [ ] Timeout config từ env: `EMBEDDING_TIMEOUT=20`
- [ ] Log prompt + embedding vào `.ai-log/`

**Commands:**
```bash
# Test Embedding
python -c "
from src.services.embedding import EmbeddingService
e = EmbeddingService()
v = e.embed_text('Xin chào')
print(len(v))  # 1536
"
```

---

## TASK-MEM-02: Vector Store Service (ChromaDB) ⬜

**Mô tả:** Wrapper cho ChromaDB — quản lý collection `contact_memory_embedding`.

**Checklist:**
- [ ] Tạo `src/services/vector_store.py` (VectorStoreService class)
- [ ] Persistent client: `./data/chroma` (config từ env: `CHROMA_PERSIST_DIR`)
- [ ] Collection: `contact_memory_embedding`
- [ ] Method `upsert(memory_id, text, embedding, metadata)`
- [ ] Method `query(query_embedding, top_k=10) -> list[dict]`
- [ ] Method `delete(memory_id)`
- [ ] Method `count() -> int`
- [ ] Metadata schema: `{ contact_id, user_id, memory_id, updated_at }`
- [ ] Test upsert + query trên collection thật

**Commands:**
```bash
# Test Vector Store
python -c "
from src.services.vector_store import VectorStoreService
vs = VectorStoreService()
vs.upsert('mem-1', 'Người này thích lập trình', [0.1]*1536, {'contact_id': 1})
print(vs.count())
print(vs.query([0.1]*1536, top_k=5))
"
```

---

## TASK-MEM-03: Memory Agent (summary + entity extraction) ⬜

**Mô tả:** Memory Agent — phân tích conversation và sinh ContactMemory.

**Checklist:**
- [ ] Tạo `src/agents/memory/` package
- [ ] Implement Prompt Template cho Memory Agent (summary + entities)
- [ ] Implement chunking utility (token-aware, ~500 token/chunk)
- [ ] Method `summarize(messages: list[Message]) -> str`
- [ ] Method `extract_entities(messages) -> dict` (company, profession, skills, interests)
- [ ] Method `calculate_relationship_score(messages) -> float` (rule-based MVP: count messages + frequency)
- [ ] Method `build_memory(contact_id) -> ContactMemory`
- [ ] Dùng LLM Gateway (`gpt-4o-mini`)
- [ ] Pydantic output validation cho entities

**Commands:**
```bash
# Test Memory Agent
python -c "
from src.agents.memory import MemoryAgent
from src.models import Message
agent = MemoryAgent()
memory = await agent.build_memory(contact_id=1)
print(memory.summary)
print(memory.company, memory.skills)
"
```

---

## TASK-MEM-04: Memory Worker (subscribe EventBus) ⬜

**Mô tả:** Background worker subscribe `EventBus` → trigger Memory Refresh theo event.

**Trigger logic:**
- `SEND_MESSAGE` → check: nếu conversation idle > 5 phút → trigger refresh
- `CLOSE_CHAT` → trigger refresh ngay
- `OPEN_AI` (manual button) → trigger refresh ngay

**Checklist:**
- [ ] Tạo `src/workers/memory_worker.py`
- [ ] Subscribe EventBus event `SEND_MESSAGE`, `CLOSE_CHAT`, `OPEN_AI`
- [ ] Check `last_message_at` của conversation — nếu idle > 5 phút → trigger
- [ ] Call Memory Agent → save ContactMemory + upsert ChromaDB
- [ ] Không block event loop (chạy async task)
- [ ] Handle LLM error gracefully (log + retry 1 lần)
- [ ] Worker khởi động trong lifespan
- [ ] Log mỗi lần refresh: `Memory refreshed for contact {id}`

**Commands:**
```bash
# Test Worker
# 1. Gửi message qua WS
# 2. Đợi 5 phút
# 3. Verify ContactMemory được tạo
sqlite3 data/app.db "SELECT id, summary FROM contact_memory;"
```

---

## TASK-MEM-05: Memory API (CRUD + refresh) ⬜

**Mô tả:** REST API cho Memory — lấy, refresh, edit.

**Endpoints:**

```
GET    /api/v1/memory/{contact_id}               — Lấy Memory hiện tại của Contact
POST   /api/v1/memory/{contact_id}/refresh       — Trigger Memory Refresh ngay
PATCH  /api/v1/memory/{contact_id}               — User edit Memory (summary, tags...)
GET    /api/v1/memory/{contact_id}/timeline      — Lấy timeline (sự kiện theo thời gian)
```

**Checklist:**
- [ ] Tạo `src/api/memory.py` router
- [ ] Inject `MemoryService` qua Depends
- [ ] Apply `get_current_user` (auth)
- [ ] `GET /memory/{id}` — trả ContactMemory JSON đầy đủ
- [ ] `POST /memory/{id}/refresh` — emit Event `OPEN_AI` → Worker xử lý
- [ ] `PATCH /memory/{id}` — update summary + tags (user edit)
- [ ] `GET /memory/{id}/timeline` — query ChromaDB sort by `updated_at`
- [ ] Response shape: `{ id, contact_id, summary, timeline, company, profession, skills, interests, relationship_score, updated_at }`

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