# Member 3 — Chat + AI Memory

> **Phụ trách:** WS-02 (Chat System) + WS-03 (AI Memory). Tích hợp WebSocket + ChromaDB cho Memory.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | Tuần 1 → Tuần 6 |
| Độ phức tạp | 🔴 Cao (WebSocket + Memory Agent + ChromaDB) |
| Phụ thuộc | Member 1 (Models + Auth), Member 4 (LLM Gateway) |
| Unblock | Member 2 (FE WebSocket client), Member 4 (Search dùng Memory) |

---

## Module của Member 3 (3 modules)

| Module | Mô tả | Tuần |
|--------|-------|------|
| **M3-CHAT-01** | Schemas + Contact API (Pydantic + CRUD Contact) | Tuần 2 ✅ |
| **M3-CHAT-02** | Chat API + WebSocket + EventBus (Conversation + Message + WS + EventBus) | Tuần 3 |
| **M3-MEM-01** | Memory Agent + Embedding + Vector Store (ChromaDB + Memory Worker) | Tuần 3 / Tuần 4 |

---

## Trạng thái hiện tại (cập nhật 03/08/2026)

- ✅ Đã đọc spec + plan.
- ✅ Setup Python 3.11 + venv.
- ✅ Test OpenAI API + Embeddings thành công.
- ✅ **GATE 1 đã nộp 02/08** (Chủ nhật tuần 2).
- ✅ M3-CHAT-01 (Schemas + Contact API) xong.
- 🟡 **Đang vào tuần 3** — M3-CHAT-02 (Chat API + WebSocket + EventBus).
- ⬜ M3-MEM-01 đang pending.

---

## Tuần 1 (23/07 – 29/07) ✅

- [x] Đọc `docs/general overview/04_Database_Design.md`
- [x] Đọc `docs/plan/ws-02-chat-system.md` + `ws-03-ai-memory.md`
- [x] Cài Python 3.11, venv, pip
- [x] Test OpenAI API thành công (`gpt-4o-mini`)
- [x] Test OpenAI Embeddings thành công (`text-embedding-3-small`)
- [x] Test LangChain import + ChromaDB local

---

## Tuần 2 (30/07 – 02/08) ✅ — GATE 1

### Module M3-CHAT-01: Schemas + Contact API ✅

- [x] Pydantic schemas: `ContactBase/Create/Update/Response` + `ConversationBase/Create/Response` + `MessageBase/Create/Response`
- [x] Enums: `MessageRole` (USER / CONTACT / AI), `ConversationStatus` (OPEN / CLOSED / ARCHIVED)
- [x] **API Contact:** `GET /contacts`, `POST /contacts`, `GET /contacts/{id}`, `PUT /contacts/{id}`, `DELETE /contacts/{id}`
- [x] Pagination `?page=1&limit=20` + Filter `?search=keyword`
- [x] Swagger docs đầy đủ

### 🚨 GATE 1 (02/08 CN) ✅
- [x] **Demo:** Test CRUD Contact qua Swagger OK
- [x] Member 2 (FE) dùng Contact API để render danh sách
- [x] Nộp GATE 1 ngày **02/08 (Chủ nhật)**

---

## Tuần 3 (03/08 – 09/08) 🟡

### Module M3-CHAT-02: Chat API + WebSocket + EventBus

- [ ] **API Conversation:** `GET /conversations`, `POST /conversations`, `GET /conversations/{id}`, `PATCH /conversations/{id}`
- [ ] **API Message:** `GET /conversations/{id}/messages`, `POST /conversations/{id}/messages`
- [ ] **WebSocket:** endpoint `/ws/chat/{conversation_id}` + Connection Manager (in-memory dict)
- [ ] Broadcast message tới các client cùng conversation
- [ ] **EventBus:** `src/events/bus.py` (asyncio.Queue + publish/subscribe)
- [ ] Background task `dispatcher_loop()` trong lifespan
- [ ] Sinh event `OPEN_CHAT` / `SEND_MESSAGE` → ghi vào `EventLog`

### Module M3-MEM-01 (phần 1): Embedding + Vector Store

- [ ] **EmbeddingService** (`embed_text` + `embed_batch` với retry + log)
- [ ] **VectorStoreService** (ChromaDB client + collection `contact_memory_embedding`)
- [ ] Method `upsert(memory_id, text, embedding, metadata)` + `query(query_embedding, top_k=10)`
- [ ] Test: embed 1 message → query → top match

### 🎯 MVP (09/08 CN)
- [ ] **Demo:** Mở 2 client WebSocket → nhắn message realtime
- [ ] Verify: Event `SEND_MESSAGE` có trong `EventLog`
- [ ] Member 4 dùng VectorStoreService cho Search

---

## Tuần 4 (10/08 – 16/08) ⬜

### Module M3-MEM-01 (phần 2): Memory Agent + Worker + API

- [ ] **Memory Agent** (`summarize` + `extract_entities` + `calculate_relationship_score`)
- [ ] Chunking utility (token-aware, ~500 token/chunk)
- [ ] **MemoryWorker** subscribe EventBus
  - Trigger refresh khi conversation idle > 5 phút
  - Trigger refresh khi `CLOSE_CHAT` event
  - Trigger refresh khi manual `OPEN_AI` event
- [ ] **API Memory:** `GET /memory/{contact_id}`, `POST /memory/{contact_id}/refresh`
- [ ] `PATCH /memory/{contact_id}` (user edit) + `GET /memory/{contact_id}/timeline`
- [ ] Integration test: gửi message qua WS → trigger Memory refresh → verify DB
- [ ] Test Memory Agent với 5 conversation mẫu (precision > 80%)

### 🚨 GATE 2 (16/08 CN)
- [ ] **Demo:** Memory Agent sinh summary + ChromaDB có embeddings + API trả JSON đúng
- [ ] Member 4 dùng Memory cho Search + Recommendation
- [ ] Verify: Conversation idle 5 phút → auto refresh ContactMemory

---

## Tuần 5 (17/08 – 23/08) ⬜

### Mở rộng `scripts/seed.py` (hỗ trợ Member 1)

- [ ] Seed 5 Contact mẫu + 10-20 messages + Memory đã generate sẵn
- [ ] Verify seed data trong DB + ChromaDB
- [ ] Test MessageService + WebSocket end-to-end
- [ ] Test API Contact/Conversation/Message/Memory endpoints
- [ ] Manual test checklist (theo WS-08 T30 → T39)
- [ ] Fix bug nếu phát hiện

### Nộp Demo Day (23/08 CN)
- [ ] Final commit `v1.0-mvp` tag

---

## Tuần 6 (24/08 – 01/09) ⬜

- [ ] **T2 (25/08):** Rehearsal lần 1 (5 phút demo) — ghi nhận feedback
- [ ] **T4 (27/08):** Rehearsal lần 2 — target chạy trơn tru 5 phút
- [ ] **T5 (28/08):** Rehearsal lần 3 — target chạy trơn tru 5 phút
- [ ] **T6 (29/08):** Final rehearsal + backup data
- [ ] **T2 (01/09) 🏆 DEMO DAY:** Demo phần Chat + Memory (2 phút trong tổng 5 phút) + Q&A

---

## ✅ Checklist cuối cùng (Tuần 6)

```
✅ M3-CHAT-01 → M3-MEM-01 (3 modules)           → DONE
✅ Contact + Conversation + Message API         → OK
✅ WebSocket realtime                           → OK
✅ EventBus + Worker                            → OK
✅ Memory Agent (summarize + entities + score)  → OK
✅ ChromaDB upsert + query                      → OK
✅ Test E2E Memory flow                         → OK
✅ Seed data (5 Contact + 10-20 messages)       → OK
```

---

## ⚠️ Vướng mắc

| Ngày | Vấn đề | Giải pháp |
|------|--------|-----------|
| (chưa có) | | |