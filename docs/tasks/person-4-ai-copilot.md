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

## Trạng thái hiện tại

- ✅ Đã đọc spec + plan.
- ✅ Setup Python 3.11 + venv.
- ✅ Test LangChain + ChromaDB local.
- 🟡 Đang vào tuần 2 — GATE 1.
- ⬜ WS-04 + WS-05 chưa code.

---

## Tuần 1 (23/07 – 29/07) ✅

- [x] Đọc `docs/general overview/03_AI_Architecture.md`
- [x] Đọc `docs/general overview/06_AI_Workflow.md`
- [x] Đọc `docs/general overview/09_AI_Agent_Architecture.md`
- [x] Đọc `docs/plan/ws-04-search-recommendation.md` + `ws-05-ai-copilot.md`
- [x] Cài LangChain + LangGraph
- [x] Test `gpt-4o-mini` qua LangChain
- [x] Test ChromaDB local (create + add + query)
- [x] Test LangGraph `StateGraph` demo

---

## Tuần 2 (30/07 – 05/08) 🟡 — GATE 1

> **Mốc:** 05/08 demo "Memory Agent generate summary từ 5 messages".

### T2 (30/07)
- [ ] Đọc kỹ `06_AI_Workflow.md` §1 (Memory workflow)
- [ ] Design Memory Prompt Template (summary + entities)

### T3 (31/07)
- [ ] Đọc kỹ `06_AI_Workflow.md` §2 (Search workflow)
- [ ] Design Search Prompt Template (re-rank prompt)

### T4 (01/08)
- [ ] Setup `src/agents/memory/` package
- [ ] Implement `memory/prompts.py` (template summary + entities)

### T5 (02/08)
- [ ] Test Memory Agent với 1 conversation mẫu (verify LLM response)
- [ ] Verify output: `summary`, `company`, `skills`, `interests`, `relationship_score`

### T6 (03/08)
- [ ] Test OpenAI Embeddings + ChromaDB upsert (local script test)
- [ ] Verify: embed 1 message → query → top match

### CN (04/08) — optional
- [ ] Design Recommendation rule engine (FOLLOWUP / REPLY / PRIORITY)
- [ ] Help Member 3 nếu cần

### T2 (05/08) 🚨 **GATE 1**
- [ ] **Demo:** Script test Memory Agent in ra summary từ 5 messages cố định
- [ ] Output JSON format đúng spec
- [ ] Cập nhật `timeline.md` tuần 2

---

## Tuần 3 (06/08 – 12/08) ⬜

### T2 (06/08)
- [ ] TASK-SR-01: Search Agent `search/query, limit)` method
- [ ] TASK-SR-01: Embed query → ChromaDB top-k (k=10)

### T3 (07/08)
- [ ] TASK-SR-01: LLM re-rank top-10 → top-5
- [ ] TASK-SR-01: Trả về `{ contact_id, name, score, explanation }`

### T4 (08/08)
- [ ] TASK-SR-02: API `GET /search?q=...&limit=5`
- [ ] TASK-SR-02: Lưu query vào `SearchHistory`

### T5 (09/08)
- [ ] TASK-SR-03: Recommendation Agent — rule-based filter
  - Contact idle > 7 ngày → FOLLOWUP
  - Contact có Memory score cao → PRIORITY
  - Message cuối chưa reply > 24h → REPLY

### T6 (10/08)
- [ ] TASK-SR-03: LLM reasoning cho Recommendation (giải thích lý do)
- [ ] TASK-SR-03: Ranking + dedup + lưu vào SQLite

### CN (11/08) — optional
- [ ] TASK-SR-04: API `GET /recommendations?status=PENDING`
- [ ] TASK-SR-04: API `POST /recommendations/{id}/accept|reject`

### T2 (12/08) 🎯 **MVP**
- [ ] **Demo:** Search "người thích lập trình Python" → top-5 Contact đúng
- [ ] Recommendation tự sinh sau Memory update
- [ ] Cập nhật `timeline.md` tuần 3

---

## Tuần 4 (13/08 – 19/08) ⬜

### T2 (13/08)
- [ ] TASK-SR-05: Insight Agent `generate_insights(contact_id)`
- [ ] TASK-SR-05: 3 loại Insight: INTEREST_PATTERN / COMMUNICATION_STYLE / RELATIONSHIP_TREND

### T3 (14/08)
- [ ] TASK-SR-06: API `GET /contacts/{id}/insights`
- [ ] TASK-SR-06: API `POST /contacts/{id}/insights/refresh`
- [ ] TASK-SR-07: Auto-create Notification khi Recommendation mới

### T4 (15/08)
- [ ] TASK-COP-01: Assistant Orchestrator (LangGraph)
- [ ] TASK-COP-01: Định nghĩa `AssistantState` TypedDict
- [ ] TASK-COP-01: Node `intent_detection` (rule-based MVP)

### T5 (16/08)
- [ ] TASK-COP-01: Node `context_builder` + `tool_selection` + `agent_execution` + `response_validator`
- [ ] TASK-COP-01: Kết nối thành StateGraph

### T6 (17/08)
- [ ] TASK-COP-02: Tools layer — `search_contact`, `get_contact_memory`, `get_recent_messages`, `recommend_reply`, `get_recommendations`

### CN (18/08) — optional
- [ ] TASK-COP-03: Tagging Agent `suggest_tags(contact_id)`
- [ ] TASK-COP-04: Connection Agent `find_connections(contact_id)`

### T2 (19/08) 🚨 **GATE 2**
- [ ] **Demo:** Copilot trả lời 5 câu hỏi mẫu:
  - "Người này là ai?" → trả Memory + Insight
  - "Tôi nên nhắn gì?" → trả Reply suggestion
  - "Tìm người thích X" → trả Search result
  - "Có Contact nào cần follow-up?" → trả Recommendation
  - "Gợi ý 3 tag" → trả Tag suggestion
- [ ] Member 2 có Copilot page + Recommendation page render đúng
- [ ] Cập nhật `timeline.md` tuần 4

---

## Tuần 5 (20/08 – 26/08) ⬜

### T2 (20/08)
- [ ] TASK-COP-03: API `GET /contacts/{id}/suggested-tags`
- [ ] TASK-COP-03: API `POST /contacts/{id}/tags` (user approve)
- [ ] TASK-COP-04: API `GET /connections/suggested`

### T3 (21/08)
- [ ] TASK-COP-05: API `POST /copilot`
- [ ] TASK-COP-05: Pydantic schemas `CopilotRequest/Response`
- [ ] TASK-COP-05: Lưu vào EventLog + log vào `.ai-log/`

### T4 (22/08)
- [ ] TASK-COP-05: Streaming response (optional — `StreamingResponse`)
- [ ] TASK-COP-05: API `POST /copilot/share` (share to conversation)

### T5 (23/08)
- [ ] TASK-TEST-02: Test Search Agent precision > 80% (5 query mẫu)
- [ ] TASK-TEST-02: Test Recommendation Agent (5 user scenarios)

### T6 (24/08)
- [ ] TASK-TEST-02: Test Copilot (5 câu hỏi mẫu)
- [ ] TASK-TEST-02: Test Tagging Agent (5 Contact mẫu)
- [ ] TASK-TEST-02: Test Connection Agent (10 Contact mẫu)

### CN (25/08) — optional
- [ ] Quay Video Demo 3 phút (record màn hình chạy demo script)
- [ ] Edit video + upload YouTube (unlisted)

### T2 (26/08) — **Nộp hồ sơ Demo Day**
- [ ] Final commit `v1.0-mvp` tag
- [ ] Nộp slide + video

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
- [ ] Demo phần AI (Search + Recommendation + Copilot) — 3 phút trong tổng 5 phút
- [ ] Q&A với BGK

---

## ✅ Checklist cuối cùng

```
Tất cả TASK-SR-* (7 tasks)          → STATUS
Tất cả TASK-COP-* (5 tasks)         → STATUS
Search Agent precision > 80%         → OK
Recommendation tự sinh               → OK
Copilot trả lời đúng 5 câu mẫu      → OK
Tagging + Connection Agent            → OK
Video demo 3 phút                    → OK
```

---

## ⚠️ Vướng mắc

| Ngày | Vấn đề | Giải pháp |
|------|--------|-----------|
| (chưa có) | | |
