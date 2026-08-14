# WS-05 — AI Copilot

> **Mục tiêu:** Hoàn thiện Assistant Orchestrator (LangGraph), AI Copilot endpoint, Tagging Agent, Connection Agent.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | WS-05 (sau WS-04) |
| Độ phức tạp | 🔴 Cao |
| Phụ thuộc | WS-03 (AI Memory), WS-04 (Search & Recommendation) |
| Unblock | WS-06 (Frontend) |

---

## Trạng thái hiện tại

| Component | Status | File |
|-----------|--------|------|
| Assistant Orchestrator | ✅ Done | `src/agents/orchestrator.py` |
| Tools layer | ✅ Done | `src/agents/tools/` |
| Tagging Agent | ✅ Done | `src/agents/tagging/agent.py` |
| Connection Agent | ✅ Done | `src/agents/connection/agent.py` |
| Copilot API | ✅ Done | `src/api/v1/copilot.py` |

---

## Orchestrator Architecture

### LangGraph StateGraph

```
┌─────────────────────────────────────────────────────────────────┐
│                 ASSISTANT ORCHESTRATOR                          │
│                    (LangGraph StateGraph)                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Intent Detection → Context Builder → Agent Selection     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                    │                                             │
│  ┌─────────────────┼─────────────────┐                       │
│  │                 │                 │                       │
│  ▼                 ▼                 ▼                       │
│ ┌───────────┐ ┌───────────┐ ┌───────────────┐               │
│ │  Memory   │ │  Search   │ │ Recommendation│               │
│ │  Agent    │ │  Agent    │ │    Agent      │               │
│ └─────┬─────┘ └─────┬─────┘ └───────┬───────┘               │
│       │             │               │                       │
│       └─────────────┼───────────────┘                       │
│                     │                                        │
│                     ▼                                        │
│           ┌─────────────────┐                                │
│           │  Merge Results   │                                │
│           └────────┬─────────┘                                │
│                    │                                          │
│                    ▼                                          │
│           ┌─────────────────┐                                │
│           │ Response         │                                │
│           │ Validator        │                                │
│           └────────┬─────────┘                                │
│                    │                                          │
│                    ▼                                          │
│           ┌─────────────────┐                                │
│           │  Return to User │                                │
│           └─────────────────┘                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Agent State

```python
# src/agents/orchestrator.py
class AgentState(TypedDict, total=False):
    # User info
    user_id: str
    conversation_id: str
    contact_id: str
    
    # Input
    user_message: str
    
    # Processing
    intent: Optional[AgentIntent]
    selected_agents: list[str]
    context: dict
    
    # Agent outputs
    memory: Optional[dict]
    search_results: Optional[list[dict]]
    recommendations: Optional[list[dict]]
    tags: Optional[list[dict]]
    connections: Optional[list[dict]]
    insights: Optional[list[dict]]
    
    # Final output
    response: Optional[str]
    error: Optional[str]
    
    # Metadata
    token_usage: dict
    latency_ms: int
```

---

## TASK-COP-01: Assistant Orchestrator ✅

**Mô tả:** LangGraph StateGraph orchestrator.

**Features:**

```python
# src/agents/orchestrator.py
class AssistantOrchestrator:
    async def process(self, message: str, context: CopilotContext) -> CopilotResponse:
        """
        1. Intent Detection (rule-based + LLM)
        2. Context Builder (Memory + recent messages)
        3. Agent Selection (based on intent)
        4. Agent Execution (parallel)
        5. Merge Results
        6. Response Generation
        7. Response Validation (security check)
        """
```

**Intent Types:**

```python
class AgentIntent(str, Enum):
    MEMORY_QUERY = "memory_query"     # "Who is this person?"
    SEARCH = "search"                # "Find AI engineers"
    RECOMMEND = "recommend"         # "Should I follow up?"
    TAG = "tag"                     # "Add tag for this contact"
    CONNECT = "connect"              # "Introduce these people"
    INSIGHT = "insight"             # "What do I know about them?"
    GENERAL = "general"              # "Hello", "Thanks"
    REPLY_SUGGEST = "reply_suggest" # "Suggest a reply"
```

---

## TASK-COP-02: Tools Layer ✅

**Mô tả:** Tools cho agents.

**Available Tools:**

```python
# src/agents/tools/
class SearchTool:
    name = "search_contact"
    description = "Search contacts using natural language"
    
class MemoryTool:
    name = "get_contact_memory"
    description = "Get the memory/knowledge about a contact"
    
class ConversationTool:
    name = "get_recent_messages"
    description = "Get recent messages from a conversation"
    
class RecommendationTool:
    name = "get_recommendations"
    description = "Get AI recommendations for contacts"
    
class TagTool:
    name = "suggest_tags"
    description = "Suggest tags for a contact"
```

---

## TASK-COP-03: Tagging Agent ✅

**Mô tả:** Entity extraction và tag suggestion.

**Features:**

```python
# src/agents/tagging/agent.py
class TaggingAgent:
    async def suggest_tags(self, contact_id: str) -> list[TagSuggestion]:
        """
        1. Get recent messages
        2. LLM extract entities:
           - companies
           - professions
           - skills
           - interests
           - topics
        3. Compare with existing tags
        4. Return new tag suggestions
        """
```

**Endpoints:**

```
GET  /api/v1/contacts/{id}/tags         — Get current tags
GET  /api/v1/contacts/{id}/suggested-tags — Get AI suggestions
POST /api/v1/contacts/{id}/tags          — Add tag
DELETE /api/v1/contacts/{id}/tags/{tag_id} — Remove tag
```

---

## TASK-COP-04: Connection Agent ✅

**Mô tả:** Contact matching và introduction suggestions.

**Features:**

```python
# src/agents/connection/agent.py
class ConnectionAgent:
    async def find_connections(self, user_id: str, top_k: int = 5) -> list[ConnectionSuggestion]:
        """
        1. Get all contacts with memory
        2. Find similar pairs based on:
           - Shared interests
           - Shared skills
           - Shared company
           - Professional complementarity
        3. LLM reason about connection
        4. Return top suggestions
        """
```

**Endpoints:**

```
GET /api/v1/connections/suggested   — Get connection suggestions
GET /api/v1/connections/contact/{id} — Get connections for contact
```

---

## TASK-COP-05: Copilot API ✅

**Mô tả:** REST API cho AI Copilot.

**Endpoints:**

```
POST /api/v1/copilot                              — Chat with Copilot
POST /api/v1/copilot/stream                       — Streaming response
POST /api/v1/copilot/share                        — Share to conversation
GET  /api/v1/copilot/intents                      — Supported intents
```

**Request/Response:**

```python
# Request
class CopilotRequest(BaseModel):
    query: str                    # User message
    context: CopilotContext | None  # Optional context
    
class CopilotContext(BaseModel):
    conversation_id: UUID | None
    contact_id: UUID | None
    include_recent_messages: bool = False
    include_memory: bool = True
    include_recommendations: bool = False

# Response
class CopilotResponse(BaseModel):
    response: str                    # AI response
    intent: str                     # Detected intent
    sources: list[Source] | None    # Evidence
    tools_used: list[str]           # Which tools were called
    token_usage: dict | None
```

**Security Features:**

- Data leak detection (prevent leaking other users' memory)
- Prompt injection detection
- Output validation

---

## Copilot Use Cases

```
┌─────────────────────────────────────────────────────────────────┐
│                      COPILOT USE CASES                           │
│                                                                 │
│  "Người này là ai?" ──────────────────────────────────► Memory │
│  "Tìm người làm AI" ──────────────────────────────► Search │
│  "Tôi nên reply thế nào?" ──────────────────────► Reply Suggest │
│  "Có ai tôi nên giới thiệu?" ──────────────────► Connection │
│  "Gợi ý tags cho người này" ─────────────────────► Tagging │
│  "Họ có gì đáng chú ý?" ────────────────────────► Insight │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Response Validation

```python
# Validation rules
class ResponseValidator:
    async def validate(self, response: str, context: AgentContext) -> ValidationResult:
        issues = []
        
        # Check for data leakage
        if self._contains_other_user_data(response, context.user_id):
            issues.append(ValidationIssue(type="data_leakage", severity="high"))
        
        # Check for prompt injection
        if self._contains_injection_patterns(response):
            issues.append(ValidationIssue(type="prompt_injection", severity="high"))
        
        return ValidationResult(
            is_valid=len([i for i in issues if i.severity == "high"]) == 0,
            issues=issues
        )
```

---

## Kết quả mong đợi sau WS-05

```
✅ LangGraph Orchestrator đầy đủ chạy được
✅ Copilot trả lời đúng các câu hỏi mẫu
✅ Tagging Agent đề xuất đúng tags
✅ Connection Agent đề xuất đúng cặp contacts
✅ Share to Conversation hoạt động
✅ Không leak memory của user khác
✅ Response validation hoạt động
```

---

## Trạng thái hoàn thành

| Task | Status | Evidence |
|------|--------|----------|
| TASK-COP-01: Assistant Orchestrator | ✅ Done | `src/agents/orchestrator.py` |
| TASK-COP-02: Tools layer | ✅ Done | `src/agents/tools/*.py` |
| TASK-COP-03: Tagging Agent | ✅ Done | `src/agents/tagging/agent.py` |
| TASK-COP-04: Connection Agent | ✅ Done | `src/agents/connection/agent.py` |
| TASK-COP-05: Copilot API | ✅ Done | `src/api/v1/copilot.py` |

---

## Reference

- [AI Agents - Assistant Orchestrator](../specs/ai-agents.md#3-assistant-orchestrator)
- [AI Agents - Tool Registry](../specs/ai-agents.md#10-tool-registry)
- [AI Agents - Tagging Agent](../specs/ai-agents.md#7-tagging-agent)
- [AI Agents - Connection Agent](../specs/ai-agents.md#8-connection-agent)
- [API - Copilot Endpoints](../specs/api.md#9-copilot-api)

---

*Version: 2.0 (Specv2 aligned)*
*Last Updated: 2026-08-14*
