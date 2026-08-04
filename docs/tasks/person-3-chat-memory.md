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

## Trạng thái hiện tại

- ✅ Đã đọc spec + plan.
- ✅ Setup Python 3.11 + venv.
- ✅ Test OpenAI API thành công.
- 🟡 Đang vào tuần 2 — GATE 1.
- ⬜ WS-02 chưa bắt đầu code.

---

## Tuần 1 (23/07 – 29/07) ✅

- [x] Đọc `docs/general overview/04_Database_Design.md`
- [x] Đọc `docs/plan/ws-02-chat-system.md` + `ws-03-ai-memory.md`
- [x] Cài Python 3.11, venv, pip
- [x] Test OpenAI API thành công (`gpt-4o-mini`)
- [x] Test OpenAI Embeddings thành công (`text-embedding-3-small`)
- [x] Test LangChain import (TextLoader, OpenAIChat)

---

## Tuần 2 (30/07 – 05/08) 🟡 — GATE 1

> **Mốc:** 05/08 demo Chat gửi/nhận qua WS.

### T2 (30/07)
- [ ] TASK-CHAT-01: Pydantic schemas `ContactBase/Create/Update/Response`
- [ ] TASK-CHAT-01: Pydantic schemas `ConversationBase/Create/Response`

### T3 (31/07)
- [ ] TASK-CHAT-01: Pydantic schemas `MessageBase/Create/Response`
- [ ] TASK-CHAT-01: Enum `MessageRole` (USER / CONTACT / AI)
- [ ] TASK-CHAT-01: Enum `ConversationStatus` (OPEN / CLOSED / ARCHIVED)
- [ ] TASK-CHAT-02: API `GET /contacts` + `POST /contacts` (thêm swagger docs)

### T4 (01/08)
- [ ] TASK-CHAT-02: API `GET /contacts/{id}` + `PUT /contacts/{id}` + `DELETE /contacts/{id}`
- [ ] TASK-CHAT-02: Pagination `?page=1&limit=20` + Filter `?search=keyword`
- [ ] TASK-CHAT-03: API `GET /conversations` + `POST /conversations`

### T5 (02/08)
- [ ] TASK-CHAT-03: API `GET /conversations/{id}` + `PATCH /conversations/{id}`
- [ ] TASK-CHAT-03: Sinh Event `OPEN_CHAT` khi tạo conversation
- [ ] TASK-CHAT-04: API `GET /conversations/{id}/messages`

### T6 (03/08)
- [ ] TASK-CHAT-04: API `POST /conversations/{id}/messages`
- [ ] TASK-CHAT-04: Sinh Event `SEND_MESSAGE` qua EventBus
- [ ] TASK-CHAT-09: WebSocket endpoint `/ws/chat/{conversation_id}` (skeleton)

### CN (04/08) — optional
- [ ] TASK-CHAT-05: ConnectionManager class (in-memory dict)
- [ ] TASK-CHAT-05: Broadcast message tới các client cùng conversation

### T2 (05/08) 🚨 **GATE 1**
- [ ] **Demo:** Mở 2 client WebSocket → gửi message từ client 1 → client 2 nhận realtime
- [ ] Verify: Event `SEND_MESSAGE` có trong `EventLog`
- [ ] Cập nhật `timeline.md` tuần 2

---

## Tuần 3 (06/08 – 12/08) ⬜

### T2 (06/08)
- [ ] TASK-CHAT-06: `src/events/bus.py` (EventBus singleton + asyncio.Queue)
- [ ] TASK-CHAT-06: Method `publish(event_type, payload)` + `subscribe(event_type, handler)`

### T3 (07/08)
- [ ] TASK-CHAT-06: Background task `dispatcher_loop()` trong lifespan
- [ ] TASK-CHAT-06: Mỗi event ghi vào `EventLog`
- [ ] TASK-MEM-01: EmbeddingService (`embed_text` + `embed_batch`)

### T4 (08/08)
- [ ] TASK-MEM-01: EmbeddingService retry + cache + log
- [ ] TASK-MEM-02: VectorStoreService (ChromaDB client + collection `contact_memory_embedding`)

### T5 (09/08)
- [ ] TASK-MEM-02: Method `upsert(memory_id, text, embedding, metadata)`
- [ ] TASK-MEM-02: Method `query(query_embedding, top_k=10)`

### T6 (10/08)
- [ ] TASK-MEM-03: Memory Agent (`summarize` + `extract_entities` + `calculate_relationship_score`)
- [ ] TASK-MEM-03: Chunking utility (token-aware, ~500 token/chunk)

### CN (11/08) — optional
- [ ] TASK-MEM-03: Test Memory Agent với 5 conversation mẫu
- [ ] Help Member 1 với test repository

### T2 (12/08) 🎯 **MVP**
- [ ] **Demo:** Conversation mới → gửi 5 messages → đợi 5 phút → ContactMemory tự động sinh
- [ ] Verify: ChromaDB collection `contact_memory_embedding` có embeddings
- [ ] Cập nhật `timeline.md` tuần 3

---

## Tuần 4 (13/08 – 19/08) ⬜

### T2 (13/08)
- [ ] TASK-MEM-04: MemoryWorker subscribe EventBus
- [ ] TASK-MEM-04: Trigger refresh khi conversation idle > 5 phút

### T3 (14/08)
- [ ] TASK-MEM-04: Trigger refresh khi `CLOSE_CHAT` event
- [ ] TASK-MEM-04: Trigger refresh khi `OPEN_AI` event (manual button)

### T4 (15/08)
- [ ] TASK-MEM-05: API `GET /memory/{contact_id}` (full JSON)
- [ ] TASK-MEM-05: API `POST /memory/{contact_id}/refresh`

### T5 (16/08)
- [ ] TASK-MEM-05: API `PATCH /memory/{contact_id}` (user edit)
- [ ] TASK-MEM-05: API `GET /memory/{contact_id}/timeline`

### T6 (17/08)
- [ ] TASK-MEM-21: Test Memory Agent end-to-end
- [ ] TASK-MEM-20: Test ChromaDB upsert + query

### CN (18/08) — optional
- [ ] Integration test: gửi message qua WS → trigger Memory refresh → verify DB

### T2 (19/08) 🚨 **GATE 2**
- [ ] **Demo:** Memory Agent sinh summary + ChromaDB có embeddings + API trả JSON đúng
- [ ] Member 4 dùng Memory cho Search + Recommendation
- [ ] Cập nhật `timeline.md` tuần 4

---

## Tuần 5 (20/08 – 26/08) ⬜

### T2 (20/08)
- [ ] TASK-TEST-02: Test Memory Agent với 5 conversation mẫu (precision > 80%)
- [ ] TASK-TEST-01: Test MessageService + WebSocket

### T3 (21/08)
- [ ] TASK-TEST-01: Test API Contact/Conversation/Message endpoints
- [ ] TASK-TEST-01: Test API Memory endpoint

### T4 (22/08)
- [ ] TASK-TEST-07: Mở rộng `scripts/seed.py` — tạo 5 Contact + 10-20 messages + Memory mẫu
- [ ] TASK-TEST-07: Verify seed data trong DB

### T5 (23/08)
- [ ] Manual test checklist (theo WS-08-T30 → T39)
- [ ] Fix bug nếu phát hiện

### T6 (24/08)
- [ ] Help Member 1 với Integration test
- [ ] Help Member 2 với WebSocket client integration

### CN (25/08) — optional
- [ ] Buffer / fix bug

### T2 (26/08) — **Nộp hồ sơ Demo Day**
- [ ] Final commit `v1.0-mvp` tag
- [ ] Verify Memory + Chat end-to-end

---

## Tuần 6 (27/08 – 01/09) ⬜

### T2 (27/08)
- [ ] Rehearsal lần 1 (toàn nhóm) — 5 phút demo
- [ ] Ghi nhận feedback

### T4 (29/08)
- [ ] Rehearsal lần 2 — target chạy trơn tru 5 phút

### T5 (30/08)
- [ ] Rehearsal lần 3 — target chạy trơn tru 5 phút

### T6 (31/08)
- [ ] Final rehearsal + Backup data
- [ ] Chuẩn bị: laptop + demo script in sẵn

### T2 (01/09) 🏆 **DEMO DAY**
- [ ] Demo phần Chat + Memory (2 phút trong tổng 5 phút)
- [ ] Q&A với BGK

---

## ✅ Checklist cuối cùng

```
Tất cả TASK-CHAT-* (6 tasks)        → STATUS
Tất cả TASK-MEM-* (5 tasks)         → STATUS
WebSocket realtime                   → OK
Memory Agent                         → OK
ChromaDB upsert + query              → OK
EventBus + Worker                    → OK
Test E2E Memory flow                 → OK
Seed data                            → OK
```

---

## ⚠️ Vướng mắc

| Ngày | Vấn đề | Giải pháp |
|------|--------|-----------|
| (chưa có) | | |
