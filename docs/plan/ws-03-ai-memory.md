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

| Component | Status | File |
|-----------|--------|------|
| Embedding Service | ✅ Done | `src/services/llm.py` |
| Vector Store (ChromaDB) | ✅ Done | `src/services/vector_store.py` |
| Memory Agent | ✅ Done | `src/agents/memory/agent.py` |
| Memory Worker | ✅ Done | `src/workers/memory_worker.py` |
| Memory API | ✅ Done | `src/api/v1/memory.py` |

---

## Memory Architecture

### Memory Types

```
┌─────────────────────────────────────────────────────────────────┐
│                         MEMORY LAYER                             │
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐           │
│  │  CONVERSATION        │    │  CONTACT            │           │
│  │  MEMORY              │    │  MEMORY             │           │
│  │─────────────────────│    │────────────────────│           │
│  │ summary             │    │ summary            │           │
│  │ current_topics      │    │ profession         │           │
│  │ decisions           │    │ company            │           │
│  │ last_processed_id   │    │ skills (JSON)      │           │
│  │                      │    │ interests (JSON)   │           │
│  │                      │    │ timeline (JSON)    │           │
│  │                      │    │ relationship_score │           │
│  │                      │    │ insights (JSON)    │           │
│  └─────────────────────┘    └─────────────────────┘           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  VECTOR STORAGE (ChromaDB)                              │   │
│  │  - contact_memory_embeddings                             │   │
│  │  - message_embeddings                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Memory Workflow

```
Message Created
       │
       ▼
Increment pending_message_count
       │
       ▼
Trigger Manager
       │
Condition satisfied?
       │
YES
       │
       ▼
Fetch unprocessed messages
       │
       ▼
Load previous Memory (if exists)
       │
       ▼
LLM: Summarize + Extract Entities
       │
       ▼
Update ContactMemory (merge)
       │
       ▼
Generate Embedding
       │
       ▼
Upsert to ChromaDB
       │
       ▼
Reset pending count
       │
       ▼
Update last_processed_message_id
```

---

## TASK-MEM-01: Embedding Service ✅

**Mô tả:** Wrapper cho OpenAI Embeddings API.

**Implementation:**

```python
# LLMGateway.embed() in src/services/llm.py
async def embed(self, texts: list[str]) -> list[list[float]]:
    """Embed texts using OpenAI embeddings."""
    response = await self.client.embeddings.create(
        model=settings.embedding_model,
        input=texts
    )
    return [item.embedding for item in response.data]
```

**Features:**

- Model: `text-embedding-3-small` (1536 dimensions)
- Batch support
- Retry with exponential backoff
- Logging to `.ai-log/`

---

## TASK-MEM-02: Vector Store Service (ChromaDB) ✅

**Mô tả:** Wrapper cho ChromaDB.

**Implementation:**

```python
# src/services/vector_store.py
class VectorStoreService:
    def __init__(self, persist_dir: str = "./data/chroma"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="contact_memory_embeddings",
            metadata={"hnsw:space": "cosine"}
        )
    
    async def upsert(self, memory_id: str, text: str, embedding: list[float], metadata: dict)
    async def query(self, query_embedding: list[float], top_k: int = 10) -> list[dict]
    async def delete(self, memory_id: str)
```

**Collections:**

- `contact_memory_embeddings` — Contact memory vectors
- `message_embeddings` — Message chunk vectors

---

## TASK-MEM-03: Memory Agent ✅

**Mô tả:** Memory Agent phân tích conversation và sinh ContactMemory.

**Features:**

```python
# src/agents/memory/agent.py
class MemoryAgent:
    async def summarize(self, messages: list[Message]) -> str
    """Generate conversation summary."""
    
    async def extract_entities(self, messages: list[Message]) -> dict
    """Extract company, profession, skills, interests."""
    
    async def calculate_relationship_score(self, messages: list[Message]) -> int
    """Calculate relationship score 0-100."""
    
    async def build_timeline(self, messages: list[Message]) -> list[dict]
    """Build timeline of events."""
    
    async def process_conversation(self, conversation_id: str) -> ContactMemory
    """Full memory processing pipeline."""
```

**Prompts:**

```python
MEMORY_SUMMARY_PROMPT = """
You are a helpful assistant that summarizes conversations.

Given a conversation, create a brief summary (2-3 sentences) of what was discussed.
Focus on key topics, decisions, and important information shared.

Conversation:
{conversation_text}

Summary:
"""

ENTITY_EXTRACTION_PROMPT = """
Extract structured information from the conversation.

For each field, if information is not available, return null.
- profession: Job title or role (e.g., "AI Engineer", "Product Manager")
- company: Company name (e.g., "VinAI", "FPT")
- skills: List of technical or professional skills
- interests: List of topics the person seems interested in
"""
```

---

## TASK-MEM-04: Memory Worker ✅

**Mô tả:** Background worker subscribe EventBus.

**Trigger Conditions:**

```python
MEMORY_UPDATE_TRIGGERS = {
    "conversation_idle": timedelta(minutes=5),  # 5 min no activity
    "message_count": 20,                         # 20 new messages
    "user_request": True,                        # User clicks "Refresh"
    "batch_job": "0 2 * * *",                   # 2 AM daily
    "conversation_closed": True                   # User closes chat
}
```

**Features:**

- Subscribe to EventBus events: `SEND_MESSAGE`, `OPEN_CHAT`, `CLOSE_CHAT`, `OPEN_AI`
- Check idle time and message count
- Async processing (non-blocking)
- Retry on LLM failure (max 1 retry)
- Graceful error handling

---

## TASK-MEM-05: Memory API ✅

**Mô tả:** REST API cho Memory.

**Endpoints:**

```
GET    /api/v1/contacts/{contact_id}/memory     — Get contact memory
PUT    /api/v1/contacts/{contact_id}/memory     — Update memory (user edit)
POST   /api/v1/contacts/{contact_id}/memory/refresh — Trigger AI refresh
GET    /api/v1/contacts/{contact_id}/timeline   — Get timeline
GET    /api/v1/contacts/{contact_id}/insights    — Get insights
```

**Schemas:**

```python
# Request
class MemoryUpdateRequest(BaseModel):
    summary: str | None = None
    profession: str | None = None
    company: str | None = None
    skills: list[str] | None = None
    interests: list[str] | None = None

# Response
class MemoryResponse(BaseModel):
    id: UUID
    contact_id: UUID
    summary: str | None
    profession: str | None
    company: str | None
    skills: list[str]
    interests: list[str]
    timeline: list[dict]
    relationship_score: int
    last_discussion: str | None
    insights: list[dict]
    updated_at: datetime
```

---

## Memory Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     MESSAGE → MEMORY FLOW                       │
│                                                                 │
│  User sends message                                             │
│       │                                                        │
│       ▼                                                        │
│  ┌─────────────┐                                               │
│  │   Message   │                                               │
│  │   Created  │                                               │
│  └──────┬──────┘                                               │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                               │
│  │  Increment  │                                               │
│  │  pending_   │                                               │
│  │  count     │                                               │
│  └──────┬──────┘                                               │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐    ┌─────────────┐                            │
│  │   Check     │───►│  Condition │                            │
│  │   Triggers │    │  met?      │                            │
│  └──────┬──────┘    └──────┬──────┘                            │
│         │                   │                                   │
│         │ YES               │ NO                                │
│         ▼                   │                                   │
│  ┌─────────────┐           │                                   │
│  │   Fetch    │           │                                   │
│  │   messages │           │                                   │
│  └──────┬──────┘           │                                   │
│         │                   │                                   │
│         ▼                   │                                   │
│  ┌─────────────┐           │                                   │
│  │  Memory     │           │                                   │
│  │  Agent     │           │                                   │
│  └──────┬──────┘           │                                   │
│         │                   │                                   │
│         ▼                   │                                   │
│  ┌─────────────┐           │                                   │
│  │   Update   │           │                                   │
│  │   Memory   │           │                                   │
│  │   DB      │           │                                   │
│  └──────┬──────┘           │                                   │
│         │                   │                                   │
│         ▼                   │                                   │
│  ┌─────────────┐           │                                   │
│  │   Upsert   │           │                                   │
│  │   ChromaDB │           │                                   │
│  └─────────────┘           │                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Kết quả mong đợi sau WS-03

```
✅ Conversation mới → sau 5 phút idle → ContactMemory tự động sinh
✅ ChromaDB có embeddings cho mỗi Memory (./data/chroma)
✅ API trả Memory đúng format
✅ User có thể edit Memory qua PATCH
✅ Embedding tồn tại trong ChromaDB collection contact_memory_embeddings
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

---

## Reference

- [AI Agents - Memory Agent](../specs/ai-agents.md#4-memory-agent)
- [Database - Vector Database](../specs/database.md#4-vector-database-schema-chromadb)

---

*Version: 2.0 (Specv2 aligned)*
*Last Updated: 2026-08-14*
