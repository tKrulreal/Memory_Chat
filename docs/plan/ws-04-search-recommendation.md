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

---

## Trạng thái hiện tại

- ✅ ChromaDB + Embedding Service (từ WS-03).
- ✅ Memory + ContactMemory (từ WS-03).
- ⬜ Search Agent chưa có.
- ⬜ Recommendation Agent chưa có.
- ⬜ Insight Agent chưa có.

---

## TASK-SR-01: Search Agent (ChromaDB + LLM re-rank) ⬜

**Mô tả:** Search Agent — embed query → ChromaDB top-k → LLM re-rank → top-5.

**Checklist:**
- [ ] Tạo `src/agents/search/` package
- [ ] Implement Prompt Template cho Search Agent (re-rank prompt)
- [ ] Method `search(query: str, limit=5) -> list[SearchResult]`
- [ ] Embed query qua EmbeddingService
- [ ] Query ChromaDB top-10 (k=10)
- [ ] LLM re-rank top-10 → top-5 (dùng `gpt-4o-mini`)
- [ ] Trả về: `{ contact_id, name, score, explanation }`
- [ ] Log search query + result vào `.ai-log/`
- [ ] Test với 5 câu query mẫu (precision > 80%)

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

## TASK-SR-02: Search API ⬜

**Mô tả:** REST API cho Search — nhận query tự nhiên.

**Endpoints:**

```
GET /api/v1/search?q=...&limit=5     — Tìm Contact theo câu tự nhiên
```

**Checklist:**
- [ ] Tạo `src/api/search.py` router
- [ ] Inject `SearchAgent` qua Depends
- [ ] Validate query không rỗng (min 3 chars)
- [ ] Lưu query vào `SearchHistory` (user_id, query, results JSON, created_at)
- [ ] Trả response: `{ results: [{contact_id, name, avatar_url, score, explanation}], query }`
- [ ] Handle không có kết quả (trả empty list, không 404)

**Commands:**
```bash
# Test Search API
curl "http://localhost:8000/api/v1/search?q=ng%C6%B0%E1%BB%9Di%20th%C3%ADch%20l%E1%BA%ADp%20tr%C3%ACnh&limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

---

## TASK-SR-03: Recommendation Agent (rule-based + LLM) ⬜

**Mô tả:** Recommendation Agent — đề xuất Follow-up, Reply, Priority.

**Recommendation types:**
- `FOLLOWUP` — liên hệ lại sau X ngày idle
- `REPLY` — gợi ý reply cho message cuối
- `PRIORITY` — đánh dấu Contact quan trọng
- `CONNECTION` — đề xuất kết nối 2 Contact (thuộc WS-05)

**Checklist:**
- [ ] Tạo `src/agents/recommendation/` package
- [ ] Định nghĩa `RecommendationType` enum
- [ ] Implement rule-based filter:
  - Contact idle > 7 ngày → FOLLOWUP
  - Contact có Memory score cao → PRIORITY
  - Message cuối chưa reply > 24h → REPLY
- [ ] Implement LLM reasoning cho Recommendation (giải thích lý do)
- [ ] Implement ranking + dedup
- [ ] Lưu Recommendation vào SQLite
- [ ] Trigger Recommendation khi Memory update (subscribe EventBus)

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

## TASK-SR-04: Recommendation API (accept/reject) ⬜

**Mô tả:** REST API cho Recommendation — liệt kê, accept, reject.

**Endpoints:**

```
GET   /api/v1/recommendations?status=PENDING                — Liệt kê Recommendation của user
POST  /api/v1/recommendations/{id}/accept                  — Accept Recommendation
POST  /api/v1/recommendations/{id}/reject                  — Reject Recommendation
POST  /api/v1/recommendations/generate                     — Generate Recommendation mới
```

**Checklist:**
- [ ] Tạo `src/api/recommendations.py` router
- [ ] Inject `RecommendationService` qua Depends
- [ ] Filter: `?status=PENDING|ACCEPTED|REJECTED`
- [ ] Sort: `created_at DESC`
- [ ] `POST /accept` — update status → ACCEPTED + emit Event
- [ ] `POST /reject` — update status → REJECTED + emit Event
- [ ] `POST /generate` — trigger Recommendation Agent ngay
- [ ] Tạo Notification khi Recommendation mới (kết nối với Notification service)

**Commands:**
```bash
# Test Recommendation API
curl http://localhost:8000/api/v1/recommendations?status=PENDING \
  -H "Authorization: Bearer $TOKEN"

curl -X POST http://localhost:8000/api/v1/recommendations/1/accept \
  -H "Authorization: Bearer $TOKEN"
```

---

## TASK-SR-05: Insight Agent (behavior analysis) ⬜

**Mô tả:** Insight Agent — phân tích hành vi từ Memory, tạo Insight.

**Checklist:**
- [ ] Tạo `src/agents/insight/` package
- [ ] Implement Insight Prompt (phân tích Memory + behavior patterns)
- [ ] Method `generate_insights(contact_id) -> list[Insight]`
- [ ] Insight types:
  - `INTEREST_PATTERN` (người này quan tâm X)
  - `COMMUNICATION_STYLE` (người này thường nhắn gọn / dài)
  - `RELATIONSHIP_TREND` (relationship_score tăng/giảm)
- [ ] Lưu Insight vào `ContactMemory.insights` (JSON field)
- [ ] Insight Worker trigger mỗi Memory update
- [ ] Log insight generation vào `.ai-log/`

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

## TASK-SR-06: Insight API ⬜

**Mô tả:** REST API cho Insight — lấy Insight của Contact.

**Endpoints:**

```
GET /api/v1/contacts/{contact_id}/insights    — Lấy Insight của Contact
POST /api/v1/contacts/{contact_id}/insights/refresh   — Trigger Insight generation
```

**Checklist:**
- [ ] Thêm vào `src/api/contacts.py` (hoặc tạo `src/api/insights.py`)
- [ ] Inject `InsightAgent` qua Depends
- [ ] `GET /contacts/{id}/insights` — trả list Insight
- [ ] `POST /contacts/{id}/insights/refresh` — emit Event trigger
- [ ] Response: `{ insights: [{type, description, generated_at}] }`

**Commands:**
```bash
# Test Insight API
curl http://localhost:8000/api/v1/contacts/1/insights \
  -H "Authorization: Bearer $TOKEN"
```

---

## TASK-SR-07: SearchHistory + Notification ⬜

**Mô tả:** Hoàn thiện SearchHistory + Notification model + API.

**Checklist:**
- [ ] Verify `SearchHistory` model + `SearchHistoryRepository` đã có (từ WS-01)
- [ ] Auto-save SearchHistory mỗi lần user search
- [ ] Verify `Notification` model + `NotificationRepository` đã có (từ WS-01)
- [ ] Tạo Notification khi có Recommendation mới
- [ ] Endpoint `GET /api/v1/notifications` — liệt kê notification của user
- [ ] Endpoint `POST /api/v1/notifications/{id}/read` — đánh dấu đã đọc
- [ ] Test E2E: search → SearchHistory có record; Recommendation mới → Notification có record

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