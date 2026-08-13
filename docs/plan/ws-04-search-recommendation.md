# WS-04 — Search & Recommendation

> **Mục tiêu:** Thêm Search Agent + Recommendation Agent + Insight Agent — tìm Contact theo ngữ nghĩa và nhận đề xuất.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | WS-04 (sau WS-03) |
| Độ phức tạp | 🟡 Trung bình |
| Phụ thuộc | WS-03 (AI Memory) |
| Unblock | WS-05, WS-06 |

> **Specification Reference:** 
> - [AI Agents - Search Agent](../specs/ai-agents.md#5-search-agent)
> - [AI Agents - Recommendation Agent](../specs/ai-agents.md#6-recommendation-agent)
> - [AI Agents - Insight Agent](../specs/ai-agents.md#9-insight-agent)

---

## Trạng thái hiện tại

- ✅ ChromaDB + Embedding Service (từ WS-03).
- ✅ Memory + ContactMemory (từ WS-03).
- ✅ Search Agent (`src/agents/search/agent.py`).
- ✅ Recommendation Agent (`src/agents/recommendation/agent.py`).
- ✅ Insight Agent (`src/agents/insight/agent.py`).
- ✅ Insight Worker (`src/workers/insight_worker.py`).
- ✅ Recommendation Worker (`src/workers/recommendation_worker.py`).
- ✅ Search API (`src/api/v1/search.py`).
- ✅ Recommendation API (`src/api/v1/recommendations.py`).

---

## TASK-SR-01: Search Agent (ChromaDB + LLM re-rank) ✅

**Mô tả:** Search Agent — embed query → ChromaDB top-k → LLM re-rank → top-5.

**Checklist:**
- [x] `src/agents/search/agent.py` - SearchAgent class
- [x] Prompt Template cho Search Agent (re-rank prompt)
- [x] Method `search(query: str, limit=5) -> list[SearchResult]`
- [x] Embed query qua EmbeddingService
- [x] Query ChromaDB top-10 (k=10)
- [x] LLM re-rank top-10 → top-5 (dùng `gpt-4o-mini`)
- [x] Trả về: `{ contact_id, name, score, explanation }`
- [x] Log search query + result vào `.ai-log/search.jsonl`

**Commands:**
```bash
# Test Search Agent
python -c "
from src.agents.search import SearchAgent
agent = SearchAgent()
results = await agent.search('người thích lập trình Python', limit=5)
for r in results:
    print(r.contact_id, r.name, r.score)
"
```

---

## TASK-SR-02: Search API ✅

**Mô tả:** REST API cho Search — nhận query tự nhiên.

**Endpoints:**

```
GET /api/v1/search?q=...&limit=5     — Tìm Contact theo câu tự nhiên
```

**Checklist:**
- [x] `src/api/v1/search.py` router
- [x] Inject `SearchAgent` qua Depends
- [x] Validate query không rỗng (min 3 chars)
- [x] Lưu query vào `SearchHistory` (user_id, query, results JSON, created_at)
- [x] Trả response: `{ results: [{contact_id, name, avatar_url, score, explanation}], query }`
- [x] Handle không có kết quả (trả empty list, không 404)

**Commands:**
```bash
# Test Search API
curl "http://localhost:8000/api/v1/search?q=ng%C6%B0%E1%BB%9Di%20th%C3%ADch%20l%E1%BA%ADp%20tr%C3%ACnh&limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

---

## TASK-SR-03: Recommendation Agent (rule-based + LLM) ✅

**Mô tả:** Recommendation Agent — đề xuất Follow-up, Reply, Priority.

**Recommendation types:**
- `FOLLOWUP` — liên hệ lại sau X ngày idle
- `REPLY` — gợi ý reply cho message cuối
- `PRIORITY` — đánh dấu Contact quan trọng
- `CONNECTION` — đề xuất kết nối 2 Contact (thuộc WS-05)

**Checklist:**
- [x] `src/agents/recommendation/agent.py` - RecommendationAgent class
- [x] `RecommendationType` enum trong `src/schemas/enums.py`
- [x] Rule-based filter:
  - Contact idle > 7 ngày → FOLLOWUP
  - Contact có Memory score cao → PRIORITY
  - Message cuối chưa reply > 24h → REPLY
- [x] LLM reasoning cho Recommendation (giải thích lý do)
- [x] Dedup logic (kiểm tra PENDING trước khi tạo mới)
- [x] Lưu Recommendation vào SQLite
- [x] Recommendation Worker subscribe EventBus

**Commands:**
```bash
# Test Recommendation Agent
python -c "
from src.agents.recommendation import RecommendationAgent
agent = RecommendationAgent()
recs = await agent.generate(user_id=1)
for r in recs:
    print(r.type, r.reason)
"
```

---

## TASK-SR-04: Recommendation API (accept/reject) ✅

**Mô tả:** REST API cho Recommendation — liệt kê, accept, reject.

**Endpoints:**

```
GET   /api/v1/recommendations?status=PENDING                — Liệt kê Recommendation của user
POST  /api/v1/recommendations/{id}/accept                  — Accept Recommendation
POST  /api/v1/recommendations/{id}/reject                  — Reject Recommendation
POST  /api/v1/recommendations/generate                     — Generate Recommendation mới
```

**Checklist:**
- [x] `src/api/v1/recommendations.py` router
- [x] Filter: `?status=PENDING|ACCEPTED|REJECTED`
- [x] Sort: `created_at DESC`
- [x] `POST /accept` — update status → ACCEPTED + emit Event
- [x] `POST /reject` — update status → REJECTED + emit Event
- [x] `POST /generate` — trigger Recommendation Agent ngay
- [x] Recommendation Worker tạo Notification khi có Recommendation mới

**Commands:**
```bash
# Test Recommendation API
curl http://localhost:8000/api/v1/recommendations?status=PENDING \
  -H "Authorization: Bearer $TOKEN"

curl -X POST http://localhost:8000/api/v1/recommendations/1/accept \
  -H "Authorization: Bearer $TOKEN"
```

---

## TASK-SR-05: Insight Agent (behavior analysis) ✅

**Mô tả:** Insight Agent — phân tích hành vi từ Memory, tạo Insight.

**Checklist:**
- [x] `src/agents/insight/agent.py` - InsightAgent class
- [x] Insight Prompt (phân tích Memory + behavior patterns)
- [x] Method `generate_insights(contact_id) -> list[Insight]`
- [x] Insight types:
  - `INTEREST_PATTERN` (người này quan tâm X)
  - `COMMUNICATION_STYLE` (người này thường nhắn gọn / dài)
  - `RELATIONSHIP_TREND` (relationship_score tăng/giảm)
- [x] Lưu Insight vào `ContactMemory.insights` (JSON field)
- [x] Insight Worker trigger mỗi Memory update
- [x] `src/workers/insight_worker.py` - InsightWorker

**Commands:**
```bash
# Test Insight Agent
python -c "
from src.agents.insight import InsightAgent
agent = InsightAgent()
insights = await agent.generate_insights(contact_id=1)
for i in insights:
    print(i.type, i.description)
"
```

---

## TASK-SR-06: Insight API ✅

**Mô tả:** REST API cho Insight — lấy Insight của Contact.

**Endpoints:**

```
GET /api/v1/contacts/{contact_id}/insights    — Lấy Insight của Contact
POST /api/v1/contacts/{contact_id}/insights/refresh   — Trigger Insight generation
```

**Checklist:**
- [x] Insights endpoints trong `src/api/v1/contacts.py`
- [x] `GET /contacts/{id}/insights` — trả list Insight
- [x] `POST /contacts/{id}/insights/refresh` — emit Event trigger → InsightWorker xử lý
- [x] Response: `{ insights: [{type, description, generated_at}] }`

**Commands:**
```bash
# Test Insight API
curl http://localhost:8000/api/v1/contacts/1/insights \
  -H "Authorization: Bearer $TOKEN"
```

---

## TASK-SR-07: SearchHistory + Notification ✅

**Mô tả:** Hoàn thiện SearchHistory + Notification model + API.

**Checklist:**
- [x] `SearchHistory` model + `SearchHistoryRepository` (từ WS-01)
- [x] Auto-save SearchHistory mỗi lần user search (trong `src/api/v1/search.py`)
- [x] `Notification` model + `NotificationRepository` (từ WS-01)
- [x] Recommendation Worker tạo Notification khi có Recommendation mới
- [x] Endpoint `GET /api/v1/notifications` (trong `src/api/v1/notifications.py`)
- [x] Endpoint `POST /api/v1/notifications/{id}/read` — đánh dấu đã đọc

**Commands:**
```bash
# Test SearchHistory + Notification
sqlite3 data/app.db "SELECT * FROM search_history ORDER BY created_at DESC LIMIT 5;"
sqlite3 data/app.db "SELECT * FROM notification ORDER BY created_at DESC LIMIT 5;"
```

---

## Kết quả mong đợi sau WS-04

```
✅ Search hoạt động với câu tự nhiên (precision > 80% với 5 câu mẫu)
✅ Recommendation list hiển thị mỗi khi user mở app
✅ Recommendation tự sinh sau mỗi Memory update
✅ Accept/Reject Recommendation cập nhật DB đúng
✅ Insight xuất hiện trong ContactMemory
✅ Notification xuất hiện khi có Recommendation mới
✅ SearchHistory ghi nhận mỗi lần search
```

---

## Trạng thái hoàn thành

| Task | Status | Evidence |
|------|--------|----------|
| TASK-SR-01: Search Agent | ✅ Done | `src/agents/search/agent.py` |
| TASK-SR-02: Search API | ✅ Done | `src/api/v1/search.py` |
| TASK-SR-03: Recommendation Agent | ✅ Done | `src/agents/recommendation/agent.py` |
| TASK-SR-04: Recommendation API | ✅ Done | `src/api/v1/recommendations.py` |
| TASK-SR-05: Insight Agent | ✅ Done | `src/agents/insight/agent.py` |
| TASK-SR-06: Insight API | ✅ Done | `src/api/v1/contacts.py` (insights endpoints) |
| TASK-SR-07: SearchHistory + Notification | ✅ Done | `src/api/v1/search.py`, `recommendations.py`, `notifications.py` |