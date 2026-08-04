# Member 4 — Search & Recommendation + AI Copilot

> **Phụ trách:** WS-04 (Search & Recommendation) + WS-05 (AI Copilot + Tagging + Connection).

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | Tuần 1 → Tuần 6 |
| Độ phức tạp | 🔴 Cao (nhiều Agent + Orchestrator) |
| Phụ thuộc | Member 1 (LLM Gateway), Member 3 (Memory + ChromaDB) |
| Unblock | Demo Material |

---

## Module của Member 4 (5 modules)

| Module | Mô tả | Tuần |
|--------|-------|------|
| **M4-AI-01** | Memory Agent prompt + Test setup (prompt template + LLM test) | Tuần 2 ✅ |
| **M4-SR-01** | Search Agent + API (embed query + ChromaDB top-k + LLM re-rank) | Tuần 3 |
| **M4-SR-02** | Recommendation + Insight Agent + Notification | Tuần 3 / Tuần 4 |
| **M4-COP-01** | Copilot Orchestrator + Tools (LangGraph + intent detection) | Tuần 4 |
| **M4-COP-02** | Copilot API + Tagging + Connection Agent + Video demo | Tuần 4 / Tuần 5 |

---

## Trạng thái hiện tại (cập nhật 03/08/2026)

- ✅ Đã đọc spec + plan.
- ✅ Setup Python 3.11 + venv.
- ✅ Test LangChain + ChromaDB + LangGraph local.
- ✅ **GATE 1 đã nộp 02/08** (Chủ nhật tuần 2).
- ✅ M4-AI-01 (Memory Agent prompt template + test) xong.
- 🟡 **Đang vào tuần 3** — M4-SR-01 (Search Agent + API).
- ⬜ M4-SR-02 → M4-COP-02 đang pending.

---

## Tuần 1 (23/07 – 29/07) ✅

- [x] Đọc `docs/general overview/03_AI_Architecture.md`, `06_AI_Workflow.md`, `09_AI_Agent_Architecture.md`
- [x] Đọc `docs/plan/ws-04-search-recommendation.md` + `ws-05-ai-copilot.md`
- [x] Cài LangChain + LangGraph + ChromaDB
- [x] Test `gpt-4o-mini` qua LangChain
- [x] Test LangGraph `StateGraph` demo

---

## Tuần 2 (30/07 – 02/08) ✅ — GATE 1

### Module M4-AI-01: Memory Agent prompt + Test setup ✅

- [x] Đọc kỹ `06_AI_Workflow.md` §1 (Memory workflow)
- [x] Design Memory Prompt Template (summary + entities + relationship_score)
- [x] Setup `src/agents/memory/` package + `memory/prompts.py`
- [x] Test Memory Agent với 1 conversation mẫu (verify LLM response JSON đúng format)
- [x] Test OpenAI Embeddings + ChromaDB upsert local (embed 1 message → query → top match)
- [x] Design Recommendation rule engine (FOLLOWUP / REPLY / PRIORITY)

### 🚨 GATE 1 (02/08 CN) ✅
- [x] **Demo:** Script test Memory Agent in ra summary từ 5 messages cố định
- [x] Output JSON format đúng spec (summary, company, skills, interests, relationship_score)
- [x] Nộp GATE 1 ngày **02/08 (Chủ nhật)**

---

## Tuần 3 (03/08 – 09/08) 🟡

### Module M4-SR-01: Search Agent + API

- [ ] **Search Agent** method `search(query, limit)`: embed query → ChromaDB top-k (k=10)
- [ ] LLM re-rank top-10 → top-5 với explanation
- [ ] Trả về JSON `{ contact_id, name, score, explanation }`
- [ ] **API `GET /search?q=...&limit=5`** + lưu vào `SearchHistory`

### Module M4-SR-02 (phần 1): Recommendation Agent + API

- [ ] **Recommendation Agent** — rule-based filter:
  - Contact idle > 7 ngày → FOLLOWUP
  - Contact có Memory score cao → PRIORITY
  - Message cuối chưa reply > 24h → REPLY
- [ ] LLM reasoning cho Recommendation (giải thích lý do)
- [ ] Ranking + dedup + lưu vào SQLite
- [ ] **API `GET /recommendations?status=PENDING`** + `POST /recommendations/{id}/accept|reject`

### 🎯 MVP (09/08 CN)
- [ ] **Demo:** Search "người thích lập trình Python" → top-5 Contact đúng
- [ ] Recommendation tự sinh sau Memory update
- [ ] Verify: precision > 80% với 5 query mẫu

---

## Tuần 4 (10/08 – 16/08) ⬜

### Module M4-SR-02 (phần 2): Insight Agent + Notification

- [ ] **Insight Agent** `generate_insights(contact_id)` — 3 loại:
  - INTEREST_PATTERN: chủ đề hay nhắc đến
  - COMMUNICATION_STYLE: formal/casual/friendly
  - RELATIONSHIP_TREND: tăng/giảm/ổn định
- [ ] **API `GET /contacts/{id}/insights`** + `POST /contacts/{id}/insights/refresh`
- [ ] Auto-create Notification khi Recommendation mới

### Module M4-COP-01: Copilot Orchestrator + Tools

- [ ] **Assistant Orchestrator** (LangGraph)
  - Định nghĩa `AssistantState` TypedDict
  - Node `intent_detection` (rule-based MVP)
  - Node `context_builder` + `tool_selection` + `agent_execution` + `response_validator`
  - Kết nối thành StateGraph
- [ ] **Tools layer:**
  - `search_contact(query, limit)`
  - `get_contact_memory(contact_id)`
  - `get_recent_messages(contact_id, limit)`
  - `recommend_reply(contact_id, last_message)`
  - `get_recommendations(status)`

### 🚨 GATE 2 (16/08 CN)
- [ ] **Demo:** Copilot trả lời 5 câu hỏi mẫu:
  - "Người này là ai?" → Memory + Insight
  - "Tôi nên nhắn gì?" → Reply suggestion
  - "Tìm người thích X" → Search result
  - "Có Contact nào cần follow-up?" → Recommendation
  - "Gợi ý 3 tag" → Tag suggestion
- [ ] Member 2 (FE) có Copilot page + Recommendation page render đúng

---

## Tuần 5 (17/08 – 23/08) ⬜

### Module M4-COP-02: Copilot API + Tagging + Connection + Video

- [ ] **API `POST /copilot`** với Pydantic `CopilotRequest/Response`
- [ ] Lưu vào EventLog + log prompt/response vào `.ai-log/`
- [ ] Streaming response (optional — `StreamingResponse`)
- [ ] API `POST /copilot/share` (share Copilot answer to Conversation)
- [ ] **Tagging Agent** `suggest_tags(contact_id)` — 3-5 tag mỗi Contact
- [ ] API `GET /contacts/{id}/suggested-tags` + `POST /contacts/{id}/tags` (approve)
- [ ] **Connection Agent** `find_connections(contact_id)` — gợi ý người liên quan
- [ ] API `GET /connections/suggested`
- [ ] **AI eval:** Test Search (precision > 80%), Recommendation (5 user scenarios), Copilot (5 câu), Tagging (5 Contact), Connection (10 Contact)
- [ ] Quay Video Demo 3 phút (record màn hình chạy demo script) + upload YouTube unlisted

### Nộp Demo Day (23/08 CN)
- [ ] Final commit `v1.0-mvp` tag + Nộp slide + video

---

## Tuần 6 (24/08 – 01/09) ⬜

- [ ] **T2 (25/08):** Rehearsal lần 1 (5 phút demo) — ghi nhận feedback
- [ ] **T4 (27/08):** Rehearsal lần 2 — target chạy trơn tru 5 phút
- [ ] **T5 (28/08):** Rehearsal lần 3 — target chạy trơn tru 5 phút
- [ ] **T6 (29/08):** Final rehearsal + backup data
- [ ] **T2 (01/09) 🏆 DEMO DAY:** Demo phần AI (Search + Recommendation + Copilot) — 3 phút trong tổng 5 phút + Q&A

---

## ✅ Checklist cuối cùng (Tuần 6)

```
✅ M4-AI-01 → M4-COP-02 (5 modules)             → DONE
✅ Search Agent precision > 80%                  → OK
✅ Recommendation tự sinh                        → OK
✅ Copilot trả lời đúng 5 câu mẫu               → OK
✅ Insight Agent (3 loại)                        → OK
✅ Tagging + Connection Agent                    → OK
✅ Video demo 3 phút (YouTube unlisted)          → OK
```

---

## ⚠️ Vướng mắc

| Ngày | Vấn đề | Giải pháp |
|------|--------|-----------|
| (chưa có) | | |