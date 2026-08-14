# WS-04 — Search & Recommendation

> **Mục tiêu:** Semantic Search + Recommendation System + Insight Analysis.

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

| Component | Status | File |
|-----------|--------|------|
| Search Agent | ✅ Done | `src/agents/search/agent.py` |
| Search API | ✅ Done | `src/api/v1/search.py` |
| Recommendation Agent | ✅ Done | `src/agents/recommendation/agent.py` |
| Recommendation API | ✅ Done | `src/api/v1/recommendations.py` |
| Recommendation Worker | ✅ Done | `src/workers/recommendation_worker.py` |
| Insight Agent | ✅ Done | `src/agents/insight/agent.py` |
| Insight Worker | ✅ Done | `src/workers/insight_worker.py` |
| SearchHistory tracking | ✅ Done | `src/services/search.py` |

---

## Search Architecture

### Search Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      SEMANTIC SEARCH FLOW                        │
│                                                                 │
│  User enters natural query                                       │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────┐                                               │
│  │  Embed     │  ── text-embedding-3-small ──► 1536 dim     │
│  │  Query     │                                               │
│  └──────┬──────┘                                               │
│         │                                                         │
│         ▼                                                         │
│  ┌─────────────┐                                               │
│  │  ChromaDB  │  ── cosine similarity ──► Top-K candidates  │
│  │  Search    │                                               │
│  └──────┬──────┘                                               │
│         │                                                         │
│         ▼                                                         │
│  ┌─────────────┐                                               │
│  │  Get       │  ── fetch contact details ──► enriched list  │
│  │  Details   │                                               │
│  └──────┬──────┘                                               │
│         │                                                         │
│         ▼                                                         │
│  ┌─────────────┐                                               │
│  │  LLM       │  ── re-rank + explain ──► Final results     │
│  │  Re-rank   │                                               │
│  └──────┬──────┘                                               │
│         │                                                         │
│         ▼                                                         │
│  ┌─────────────┐                                               │
│  │  Save to    │  ── SearchHistory table ──► audit log       │
│  │  History   │                                               │
│  └─────────────┘                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## TASK-SR-01: Search Agent ✅

**Mô tả:** Semantic search với ChromaDB + LLM re-rank.

**Features:**

```python
# src/agents/search/agent.py
class SearchAgent:
    async def search(self, query: str, user_id: str, limit: int = 5) -> SearchResponse:
        """
        1. Embed query
        2. Query ChromaDB top-K
        3. Get contact details
        4. LLM re-rank to top-5
        5. Generate explanation
        """
```

**Example Queries:**

| Query | Meaning | Result |
|-------|---------|--------|
| "Find AI engineers" | Semantic: skills ∝ "AI" | Contacts with AI skill |
| "People I met at startup event" | Semantic: context ∝ "startup" | Relevant contacts |
| "Who wants to hire?" | Semantic: interest ∝ "hiring" | Contacts hiring |

---

## TASK-SR-02: Search API ✅

**Mô tả:** REST API cho Search.

**Endpoints:**

```
GET /api/v1/search?q=...&limit=5   — Semantic search
GET /api/v1/search/history          — Search history
```

**Features:**

- Validate query (min 3 chars)
- Save to SearchHistory
- Return results with explanation

---

## Recommendation Architecture

### Recommendation Types

```
┌─────────────────────────────────────────────────────────────────┐
│                   RECOMMENDATION TYPES                            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  FOLLOWUP   │  │    REPLY    │  │   PRIORITY  │         │
│  │─────────────│  │─────────────│  │─────────────│         │
│  │ Re-contact  │  │ Suggest     │  │ High-value  │         │
│  │ after X    │  │ response    │  │ contacts    │         │
│  │ days       │  │ for message │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ CONNECTION  │  │     TAG     │  │    MERGE    │         │
│  │─────────────│  │─────────────│  │─────────────│         │
│  │ Introduce   │  │ Suggest     │  │ Potential   │         │
│  │ two people │  │ tags for    │  │ duplicate   │         │
│  │             │  │ contact     │  │ contacts    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## TASK-SR-03: Recommendation Agent ✅

**Mô tả:** Rule-based + LLM recommendation generation.

**Features:**

```python
# src/agents/recommendation/agent.py
class RecommendationAgent:
    async def generate(self, user_id: str) -> list[Recommendation]:
        """
        1. Get all contacts with memory
        2. Rule-based candidate generation:
           - FOLLOWUP: idle > 14 days
           - REPLY: last message from contact > 24h
           - PRIORITY: high relationship_score
        3. LLM reasoning for explanation
        4. Dedup (check PENDING)
        5. Save to DB
        """
```

---

## TASK-SR-04: Recommendation API ✅

**Mô tả:** REST API cho Recommendation.

**Endpoints:**

```
GET    /api/v1/recommendations            — List recommendations
POST   /api/v1/recommendations/generate  — Generate new recommendations
POST   /api/v1/recommendations/{id}/accept  — Accept
POST   /api/v1/recommendations/{id}/reject   — Reject
```

**Features:**

- Filter by status (PENDING, ACCEPTED, REJECTED)
- Sort by created_at DESC
- Accept/Reject updates status and emits event
- Notification on new recommendation

---

## TASK-SR-05: Insight Agent ✅

**Mô tả:** Behavioral analysis từ contact data.

**Insight Types:**

```python
class InsightType(str, Enum):
    BEHAVIOR = "behavior"           # "Responds quickly in mornings"
    PATTERN = "pattern"           # "Discusses AI every week"
    PREFERENCE = "preference"      # "Prefers concise messages"
    OPPORTUNITY = "opportunity"   # "Might be interested in X"
    RISK = "risk"                # "Less engaged recently"
    FACT = "fact"                # "Works at VinAI as AI Engineer"
```

**Features:**

```python
# src/agents/insight/agent.py
class InsightAgent:
    async def generate_insights(self, contact_id: str) -> list[Insight]:
        """
        1. Get contact memory
        2. Get recent messages
        3. Analyze patterns:
           - Communication frequency
           - Topic trends
           - Engagement levels
        4. Generate insights via LLM
        5. Save to ContactMemory.insights
        """
```

---

## TASK-SR-06: Insight API ✅

**Mô tả:** REST API cho Insights.

**Endpoints:**

```
GET    /api/v1/contacts/{id}/insights           — Get insights
POST   /api/v1/contacts/{id}/insights/refresh   — Trigger refresh
```

---

## TASK-SR-07: SearchHistory + Notification ✅

**Mô tả:** Audit logging + User notifications.

**SearchHistory:**

```python
class SearchHistory(Base):
    id: UUID
    user_id: FK(users.id)
    query: str
    result_count: int
    created_at: datetime
```

**Notification:**

```python
class Notification(Base):
    id: UUID
    user_id: FK(users.id)
    type: str  # RECOMMENDATION, FOLLOWUP, MEMORY_UPDATED
    title: str
    content: str
    status: str  # UNREAD, READ
    created_at: datetime
```

**Endpoints:**

```
GET    /api/v1/notifications              — List notifications
PATCH  /api/v1/notifications/{id}/read   — Mark as read
GET    /api/v1/search/history            — Search history
```

---

## Recommendation Worker Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                RECOMMENDATION WORKER FLOW                       │
│                                                                 │
│  Trigger: MEMORY_UPDATED event OR periodic (daily)            │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────┐                                               │
│  │  Get all   │                                               │
│  │  contacts  │                                               │
│  └──────┬──────┘                                               │
│         │                                                         │
│         ▼                                                         │
│  ┌─────────────┐                                               │
│  │  Analyze   │                                               │
│  │  each     │                                               │
│  │  contact  │                                               │
│  └──────┬──────┘                                               │
│         │                                                         │
│         ▼                                                         │
│  ┌─────────────┐    ┌─────────────┐                           │
│  │  Generate  │───►│  Dedup      │                           │
│  │  candidates│    │  (PENDING)  │                           │
│  └──────┬──────┘    └──────┬──────┘                           │
│         │                    │                                  │
│         └──────────┬─────────┘                                  │
│                    │                                            │
│                    ▼                                            │
│  ┌─────────────┐                                               │
│  │  Save to   │                                               │
│  │  DB        │                                               │
│  └──────┬──────┘                                               │
│         │                                                         │
│         ▼                                                         │
│  ┌─────────────┐                                               │
│  │  Create   │                                               │
│  │  Notification │                                            │
│  └─────────────┘                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Kết quả mong đợi sau WS-04

```
✅ Search hoạt động với câu tự nhiên
✅ Recommendation list hiển thị (PENDING)
✅ Accept/Reject cập nhật DB đúng
✅ Insight xuất hiện trong ContactMemory
✅ Notification khi có Recommendation mới
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
| TASK-SR-07: SearchHistory + Notification | ✅ Done | `src/api/v1/search.py`, `notifications.py` |

---

## Reference

- [AI Agents - Search Agent](../specs/ai-agents.md#5-search-agent)
- [AI Agents - Recommendation Agent](../specs/ai-agents.md#6-recommendation-agent)
- [AI Agents - Insight Agent](../specs/ai-agents.md#9-insight-agent)

---

*Version: 2.0 (Specv2 aligned)*
*Last Updated: 2026-08-14*
