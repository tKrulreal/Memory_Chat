# ARCHITECTURE.md — System Architecture

## MemoryChat MVP v1.0

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │    Web      │  │   Mobile    │  │  Terminal   │  │   Others    │    │
│  │   (React)   │  │  (Flutter)  │  │    (API)    │  │             │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
└─────────┼────────────────┼────────────────┼────────────────┼────────────┘
          │                │                │                │
          │     REST API   │   WebSocket    │   HTTP/REST    │
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY LAYER                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Reverse Proxy (Nginx/Caddy)                  │   │
│  │         Rate Limiting • SSL Termination • Load Balancing          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          BACKEND LAYER (FastAPI)                        │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    PRESENTATION LAYER                             │   │
│  │         REST Endpoints • WebSocket • Input Validation             │   │
│  └─────────────────────────────┬───────────────────────────────────┘   │
│                                │                                        │
│  ┌─────────────────────────────▼───────────────────────────────────┐   │
│  │                    APPLICATION LAYER                             │   │
│  │   Services: Auth, Chat, Contact, Memory, Search, Recommendation    │   │
│  │                    CopilotService, TagService                    │   │
│  └─────────────────────────────┬───────────────────────────────────┘   │
│                                │                                        │
│  ┌─────────────────────────────▼───────────────────────────────────┐   │
│  │                      DOMAIN LAYER                                │   │
│  │         Entities • Use Cases • Business Rules                     │   │
│  └─────────────────────────────┬───────────────────────────────────┘   │
│                                │                                        │
│  ┌─────────────────────────────▼───────────────────────────────────┐   │
│  │                   INFRASTRUCTURE LAYER                           │   │
│  │    Repositories • LLM Gateway • Vector DB • Event Bus            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   DATA LAYER    │   │   AI LAYER     │   │  EVENT LAYER   │
│                 │   │                 │   │                 │
│ ┌─────────────┐ │   │ ┌─────────────┐ │   │ ┌─────────────┐ │
│ │   SQLite   │ │   │ │   LangGraph │ │   │ │ EventQueue │ │
│ │ (PostgreSQL│ │   │ │ Orchestrator│ │   │ │ (Redis/Kafka│ │
│ │  Post-MVP) │ │   │ └──────┬──────┘ │   │ │   Future)  │ │
│ └─────────────┘ │   │        │         │   │ └─────────────┘ │
│ ┌─────────────┐ │   │ ┌──────▼──────┐ │   │ ┌─────────────┐ │
│ │  ChromaDB   │ │   │ │   Agents    │ │   │ │    Celery   │ │
│ │  (Qdrant    │ │   │ │  Memory     │ │   │ │  (Future)   │ │
│ │   Future)   │ │   │ │  Search     │ │   │ └─────────────┘ │
│ └─────────────┘ │   │ │  Recommend  │ │   │                 │
│ ┌─────────────┐ │   │ │  Tagging    │ │   │                 │
│ │   Neo4j     │ │   │ │  Insight    │ │   │                 │
│ │  (Future)   │ │   │ └──────┬──────┘ │   │                 │
│ └─────────────┘ │   │        │         │   │                 │
│ ┌─────────────┐ │   │ ┌──────▼──────┐ │   │                 │
│ │   Redis     │ │   │ │  LLM Gateway│ │   │                 │
│ │  (Future)   │ │   │ │  (OpenAI)   │ │   │                 │
│ └─────────────┘ │   │ └─────────────┘ │   │                 │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

---

## 2. Component Architecture

### 2.1 Frontend Architecture (Post-MVP)

```
frontend/
├── app/
│   ├── main.tsx              # Entry point
│   └── router.tsx            # React Router config
├── pages/
│   ├── Auth/                 # Login, Register
│   ├── Chat/                 # Chat list, Chat window
│   ├── Contact/              # Contact list, Profile
│   ├── Search/               # Semantic search
│   ├── Recommendation/        # Recommendation center
│   └── Copilot/              # AI Copilot UI
├── components/
│   ├── ui/                   # Base UI components
│   ├── chat/                 # Chat-specific components
│   ├── contact/              # Contact components
│   └── ai/                   # AI components (Copilot)
├── hooks/
│   ├── useAuth.ts            # Authentication hook
│   ├── useChat.ts            # Chat hook
│   ├── useWebSocket.ts       # WebSocket hook
│   └── useAI.ts              # AI Copilot hook
├── stores/
│   ├── authStore.ts          # Auth state (Zustand)
│   ├── chatStore.ts          # Chat state
│   └── uiStore.ts            # UI state
├── services/
│   ├── api.ts                # API client
│   ├── websocket.ts          # WebSocket client
│   └── ai.ts                 # AI service client
└── theme/
    ├── colors.ts             # VinUni Red palette
    └── components.ts         # Design system
```

### 2.2 Backend Architecture

```
src/
├── main.py                  # FastAPI entry point
├── config.py                # Pydantic Settings
├── api/
│   └── v1/
│       ├── __init__.py
│       ├── router.py        # Main router
│       ├── auth.py          # Auth endpoints
│       ├── chat.py           # Chat endpoints
│       ├── contact.py        # Contact endpoints
│       ├── search.py         # Search endpoints
│       ├── recommendation.py # Recommendation endpoints
│       ├── copilot.py        # Copilot endpoints
│       └── memory.py         # Memory endpoints
├── core/
│   ├── __init__.py
│   ├── database.py          # Database connection
│   ├── security.py          # JWT, password hashing
│   ├── dependencies.py      # FastAPI dependencies
│   └── exceptions.py         # Custom exceptions
├── models/
│   ├── __init__.py
│   ├── user.py              # User model
│   ├── contact.py           # Contact model
│   ├── conversation.py     # Conversation model
│   ├── message.py           # Message model
│   └── memory.py            # Memory model
├── schemas/
│   ├── __init__.py
│   ├── auth.py              # Auth Pydantic schemas
│   ├── chat.py              # Chat schemas
│   ├── contact.py           # Contact schemas
│   ├── search.py            # Search schemas
│   ├── recommendation.py    # Recommendation schemas
│   └── copilot.py           # Copilot schemas
├── repositories/
│   ├── __init__.py
│   ├── base.py              # Base repository
│   ├── user_repo.py         # User repository
│   ├── contact_repo.py      # Contact repository
│   ├── message_repo.py      # Message repository
│   └── memory_repo.py       # Memory repository
├── services/
│   ├── __init__.py
│   ├── auth_service.py      # Auth service
│   ├── chat_service.py      # Chat service
│   ├── contact_service.py   # Contact service
│   ├── memory_service.py    # Memory service
│   ├── search_service.py    # Search service
│   └── recommendation_service.py
├── agents/
│   ├── __init__.py
│   ├── graph.py             # LangGraph StateGraph
│   ├── state.py             # AgentState definition
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── agent.py         # Memory Agent
│   │   └── tools.py        # Memory tools
│   ├── search/
│   │   ├── __init__.py
│   │   ├── agent.py         # Search Agent
│   │   └── tools.py        # Search tools
│   ├── recommendation/
│   │   ├── __init__.py
│   │   ├── agent.py         # Recommendation Agent
│   │   └── tools.py        # Recommendation tools
│   ├── tagging/
│   │   ├── __init__.py
│   │   ├── agent.py         # Tagging Agent
│   │   └── tools.py        # Tagging tools
│   ├── connection/
│   │   ├── __init__.py
│   │   ├── agent.py         # Connection Agent
│   │   └── tools.py        # Connection tools
│   └── insight/
│       ├── __init__.py
│       ├── agent.py         # Insight Agent
│       └── tools.py        # Insight tools
├── workers/
│   ├── __init__.py
│   ├── memory_worker.py     # Memory update worker
│   ├── embedding_worker.py  # Embedding worker
│   └── recommendation_worker.py
├── events/
│   ├── __init__.py
│   ├── handlers.py          # Event handlers
│   └── types.py            # Event type definitions
├── tools/
│   ├── __init__.py
│   ├── registry.py          # Tool registry
│   └── memory_tools.py     # Memory-related tools
├── llm/
│   ├── __init__.py
│   ├── gateway.py           # LLM Gateway (OpenAI)
│   ├── prompts.py          # Prompt templates
│   └── validators.py       # Output validators
└── utils/
    ├── __init__.py
    ├── logger.py           # Logging setup
    └── helpers.py          # Helper functions
```

---

## 3. Data Flow Architecture

### 3.1 Message Flow

```
User A types message
        │
        ▼
┌─────────────────┐
│  Frontend sends │
│  via WebSocket  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI receives│
│  WebSocket msg  │
└────────┬────────┘
         │
         ├──────────────────────────────────────┐
         │                                      │
         ▼                                      ▼
┌─────────────────┐              ┌─────────────────┐
│  Save to SQLite │              │  Broadcast via  │
│  (Message)      │              │  WebSocket to   │
└────────┬────────┘              │  User B         │
         │                        └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Create Event   │
│  (SEND_MESSAGE) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Background     │
│  Worker picks   │
│  up event       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Memory Agent   │
│  (if triggered) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Update Contact │
│  Memory         │
└─────────────────┘
```

### 3.2 AI Request Flow

```
User requests AI Copilot
        │
        ▼
┌─────────────────┐
│  API receives   │
│  /api/v1/      │
│  copilot       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Assistant     │
│  Orchestrator  │
│  (LangGraph)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Intent         │
│  Detection       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Context        │
│  Builder        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Select Agent   │
│  (Memory/Search/│
│   Recommend)    │
└────────┬────────┘
         │
         ├────────────────────────────────────┐
         │                                    │
         ▼                                    ▼
┌─────────────────┐              ┌─────────────────┐
│  Memory Agent   │              │  Search Agent    │
│  - Get Memory   │              │  - Vector Search │
│  - Extract Info │              │  - Re-rank       │
└────────┬────────┘              └────────┬────────┘
         │                                   │
         └────────────────┬─────────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │   Merge Results     │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  LLM Response       │
              │  Generation         │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Response Validator │
              │  (Security Check)   │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Return to User     │
              └─────────────────────┘
```

---

## 4. AI Layer Architecture

### 4.1 LangGraph StateGraph

```python
# Agent State Definition
class AgentState(TypedDict):
    user_id: str
    conversation_id: str
    contact_id: str
    user_message: str
    intent: str
    selected_agent: str
    context: dict
    memory: dict
    search_results: list
    recommendations: list
    response: str
    error: str | None
```

### 4.2 Agent Orchestration Graph

```
┌─────────────┐
│    START    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Intent    │
│  Detection  │
└──────┬──────┘
       │
       ├──────────────────────┐
       │                      │
       ▼                      ▼
┌─────────────┐      ┌─────────────┐
│   Memory    │      │   Search    │
│   Intent?   │      │   Intent?   │
└──────┬──────┘      └──────┬──────┘
       │                    │
       ▼                    ▼
┌─────────────┐      ┌─────────────┐
│   Memory    │      │   Search    │
│   Agent     │      │   Agent     │
└──────┬──────┘      └──────┬──────┘
       │                    │
       └──────────┬─────────┘
                  │
       ┌──────────┴──────────┐
       │                     │
       ▼                     ▼
┌─────────────┐       ┌─────────────┐
│  Recommend  │       │   Tagging   │
│   Intent?   │       │   Intent?   │
└──────┬──────┘       └──────┬──────┘
       │                     │
       ▼                     ▼
┌─────────────┐       ┌─────────────┐
│Recommendation│      │  Tagging    │
│   Agent     │       │   Agent     │
└──────┬──────┘       └──────┬──────┘
       │                     │
       └──────────┬──────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Merge Results  │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Response       │
         │  Generation     │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │    Response    │
         │    Validator   │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │      END       │
         └─────────────────┘
```

---

## 5. Event-Driven Architecture

### 5.1 Event Types

```python
class EventType(str, Enum):
    # Chat Events
    SEND_MESSAGE = "SEND_MESSAGE"
    RECEIVE_MESSAGE = "RECEIVE_MESSAGE"
    READ_MESSAGE = "READ_MESSAGE"
    OPEN_CHAT = "OPEN_CHAT"
    CLOSE_CHAT = "CLOSE_CHAT"
    
    # AI Events
    OPEN_AI = "OPEN_AI"
    SHARE_TO_CONVERSATION = "SHARE_TO_CONVERSATION"
    
    # Search Events
    SEARCH = "SEARCH"
    
    # Contact Events
    PIN_CONTACT = "PIN_CONTACT"
    UPDATE_CONTACT = "UPDATE_CONTACT"
    
    # Tag Events
    APPROVE_TAG = "APPROVE_TAG"
    REJECT_TAG = "REJECT_TAG"
    
    # Memory Events
    MEMORY_UPDATED = "MEMORY_UPDATED"
    REFRESH_MEMORY = "REFRESH_MEMORY"
```

### 5.2 Event Flow

```
┌──────────────────────────────────────────────────────────────┐
│                      EVENT FLOW                              │
│                                                              │
│  User Action                                                 │
│       │                                                      │
│       ▼                                                      │
│  ┌────────────┐                                              │
│  │   API      │                                              │
│  │  Endpoint  │                                              │
│  └─────┬──────┘                                              │
│        │                                                     │
│        ▼                                                     │
│  ┌────────────┐     ┌────────────┐                          │
│  │   Save     │────►│   Event    │                          │
│  │   Data     │     │   Log      │                          │
│  └────────────┘     └─────┬──────┘                          │
│                           │                                  │
│                           ▼                                  │
│                    ┌────────────┐                            │
│                    │   Event    │                            │
│                    │   Queue    │                            │
│                    │ (In-memory/│                            │
│                    │  Redis)    │                            │
│                    └─────┬──────┘                            │
│                          │                                   │
│            ┌─────────────┼─────────────┐                     │
│            │             │             │                     │
│            ▼             ▼             ▼                     │
│     ┌───────────┐ ┌───────────┐ ┌───────────┐               │
│     │  Memory   │ │ Search    │ │ Recommend │               │
│     │  Worker   │ │  Worker   │ │  Worker   │               │
│     └───────────┘ └───────────┘ └───────────┘               │
│            │             │             │                      │
│            └─────────────┼─────────────┘                      │
│                          │                                   │
│                          ▼                                   │
│                   ┌────────────┐                             │
│                   │  Notify   │                             │
│                   │  (Future) │                             │
│                   └───────────┘                             │
└──────────────────────────────────────────────────────────────┘
```

---

## 6. Security Architecture

### 6.1 Authentication Flow

```
┌────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION FLOW                      │
│                                                             │
│  User                                                     │
│    │                                                       │
│    ▼                                                       │
│  ┌─────────────┐                                           │
│  │   Login     │  POST /api/v1/auth/login                  │
│  │   Request   │  { email, password }                       │
│  └──────┬──────┘                                           │
│         │                                                  │
│         ▼                                                  │
│  ┌─────────────┐                                           │
│  │   Validate  │  Check email, verify password             │
│  │   Credentials│                                          │
│  └──────┬──────┘                                           │
│         │                                                  │
│         ▼                                                  │
│  ┌─────────────┐                                           │
│  │   Generate  │  Create JWT Access + Refresh tokens       │
│  │   Tokens    │                                           │
│  └──────┬──────┘                                           │
│         │                                                  │
│         ▼                                                  │
│  ┌─────────────┐                                           │
│  │   Return    │  { access_token, refresh_token }         │
│  │   Response  │                                           │
│  └─────────────┘                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Request Authentication

```
┌────────────────────────────────────────────────────────────┐
│                  REQUEST AUTHENTICATION                     │
│                                                             │
│  Request                                                    │
│    │                                                       │
│    ▼                                                       │
│  ┌─────────────┐                                           │
│  │   Extract   │  Authorization: Bearer <token>            │
│  │   Token     │                                           │
│  └──────┬──────┘                                           │
│         │                                                  │
│         ▼                                                  │
│  ┌─────────────┐                                           │
│  │   Verify    │  Verify JWT signature, expiration         │
│  │   JWT       │                                           │
│  └──────┬──────┘                                           │
│         │                                                  │
│    ┌────┴────┐                                             │
│    │         │                                             │
│    ▼         ▼                                             │
│  ┌────┐  ┌────────┐                                        │
│  │Invalid│ │ Valid │                                       │
│  │ Token │ │ Token │                                       │
│  └──┬───┘ └───┬────┘                                       │
│     │         │                                             │
│     ▼         ▼                                             │
│  ┌──────┐  ┌────────────┐                                  │
│  │ 401  │  │ Extract    │                                  │
│  │Error │  │ user_id    │                                  │
│  └──────┘  │ from JWT   │                                  │
│            └──────┬─────┘                                  │
│                   │                                        │
│                   ▼                                        │
│            ┌────────────┐                                  │
│            │ Process    │                                  │
│            │ Request    │                                  │
│            └────────────┘                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Data Isolation

```
┌────────────────────────────────────────────────────────────┐
│                    DATA ISOLATION                           │
│                                                             │
│  User A                                                    │
│    │                                                       │
│    ▼                                                       │
│  ┌─────────────┐                                           │
│  │   Query     │  SELECT * FROM contacts                   │
│  │             │  WHERE user_id = 'A'                      │
│  └──────┬──────┘                                           │
│         │                                                  │
│         ▼                                                  │
│  ┌─────────────┐                                           │
│  │   Database  │  Automatically filtered by user_id       │
│  │   Layer     │  WHERE user_id = current_user.id         │
│  └─────────────┘                                           │
│         │                                                  │
│         ▼                                                  │
│  ┌─────────────┐                                           │
│  │   Results   │  Only User A's contacts returned         │
│  │             │  User B's data never returned to A       │
│  └─────────────┘                                           │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## 7. Scalability Architecture

### 7.1 Horizontal Scaling

```
┌────────────────────────────────────────────────────────────┐
│                  HORIZONTAL SCALING                        │
│                                                             │
│                    ┌─────────────┐                         │
│                    │   Nginx     │                         │
│                    │ Load Balancer│                        │
│                    └──────┬──────┘                         │
│                           │                                │
│         ┌─────────────────┼─────────────────┐              │
│         │                 │                 │              │
│         ▼                 ▼                 ▼              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │   FastAPI   │   │   FastAPI   │   │   FastAPI   │     │
│  │  Instance 1 │   │  Instance 2 │   │  Instance 3 │     │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘     │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           │                                │
│         ┌─────────────────┼─────────────────┐              │
│         │                 │                 │              │
│         ▼                 ▼                 ▼              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │  PostgreSQL │   │  PostgreSQL │   │  PostgreSQL │     │
│  │  Primary    │◄──│  Replica 1  │   │  Replica 2  │     │
│  └─────────────┘   └─────────────┘   └─────────────┘     │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### 7.2 Worker Scaling

```
┌────────────────────────────────────────────────────────────┐
│                    WORKER SCALING                          │
│                                                             │
│  ┌─────────────┐                                           │
│  │   Event     │                                           │
│  │   Queue     │                                           │
│  │  (Redis)    │                                           │
│  └──────┬──────┘                                           │
│         │                                                  │
│    ┌────┴────┐                                             │
│    │         │                                             │
│    ▼         ▼                                             │
│  ┌───────┐ ┌───────┐                                      │
│  │Memory │ │Memory │  ◄── Multiple workers can process    │
│  │Worker │ │Worker │      the same queue                   │
│  │   1   │ │   2   │                                      │
│  └───┬───┘ └───┬───┘                                      │
│      │         │                                           │
│      └────┬────┘                                           │
│           │                                                │
│           ▼                                                │
│    ┌─────────────┐                                         │
│    │  Database   │                                         │
│    └─────────────┘                                         │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## 8. Deployment Architecture

### 8.1 MVP Deployment

```
┌────────────────────────────────────────────────────────────┐
│                  MVP DEPLOYMENT                           │
│                                                             │
│                      Internet                              │
│                          │                                 │
│                          ▼                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                  Docker Container                     │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────────┐   │ │
│  │  │  FastAPI   │ │  LangGraph │ │   Workers      │   │ │
│  │  │  (Uvicorn) │ │  Agents    │ │   (asyncio)    │   │ │
│  │  └─────┬──────┘ └────────────┘ └────────────────┘   │ │
│  │        │                                             │ │
│  │  ┌─────┴───────────────────────────────────────┐    │ │
│  │  │              Shared Volume                   │    │ │
│  │  │  ┌─────────────┐       ┌──────────────┐    │    │ │
│  │  │  │   SQLite    │       │   ChromaDB   │    │    │ │
│  │  │  │   app.db    │       │   /data      │    │    │ │
│  │  │  └─────────────┘       └──────────────┘    │    │ │
│  │  └───────────────────────────────────────────┘    │ │
│  └──────────────────────────────────────────────────────┘ │
│                          │                                 │
│                          ▼                                 │
│                  ┌─────────────┐                          │
│                  │   OpenAI    │                          │
│                  │    API      │                          │
│                  └─────────────┘                          │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### 8.2 Post-MVP Deployment

```
┌────────────────────────────────────────────────────────────┐
│                  POST-MVP DEPLOYMENT                      │
│                                                             │
│                      Internet                              │
│                          │                                 │
│                          ▼                                 │
│               ┌──────────────────┐                        │
│               │  Load Balancer   │                        │
│               │    (Nginx)      │                        │
│               └────────┬─────────┘                        │
│                        │                                   │
│         ┌──────────────┼──────────────┐                   │
│         │              │              │                    │
│         ▼              ▼              ▼                    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐           │
│  │  FastAPI 1  │ │  FastAPI 2  │ │  FastAPI 3  │           │
│  └──────┬─────┘ └──────┬─────┘ └──────┬─────┘           │
│         │              │              │                    │
│         └──────────────┼──────────────┘                   │
│                        │                                   │
│  ┌─────────────────────┼─────────────────────┐             │
│  │                     │                      │             │
│  ▼                     ▼                      ▼             │
│ ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│ │Celery    │    │  Redis    │    │  Redis   │            │
│ │Workers   │◄───│  Stream   │◄───│  Cache   │            │
│ └──────────┘    └──────────┘    └──────────┘            │
│                        │                                 │
│         ┌──────────────┼──────────────┐                  │
│         │              │              │                   │
│         ▼              ▼              ▼                   │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│  │PostgreSQL│   │  Qdrant   │   │  Neo4j   │            │
│  └──────────┘   └──────────┘   └──────────┘            │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## 9. Monitoring Architecture

### 9.1 Observability Stack

```
┌────────────────────────────────────────────────────────────┐
│                   OBSERVABILITY                             │
│                                                             │
│  ┌───────────────┐                                         │
│  │   Metrics     │   Prometheus                            │
│  │   (Prometheus)│   - Request count                      │
│  └───────┬───────┘   - Latency                            │
│          │           - Error rate                          │
│          ▼           - Queue depth                        │
│  ┌───────────────┐                                         │
│  │   Traces      │   OpenTelemetry                         │
│  │   (OTLP)      │   - Request tracing                    │
│  └───────┬───────┘   - Span context                       │
│          │           - Correlation ID                      │
│          ▼                                               │
│  ┌───────────────┐                                         │
│  │   Logs         │   Structured Logging                   │
│  │   (ELK/Loki)  │   - JSON format                       │
│  └───────────────┘   - Log levels                         │
│          │                                               │
│          ▼                                               │
│  ┌───────────────┐                                         │
│  │   Dashboards  │   Grafana                              │
│  │   (Grafana)   │   - System overview                    │
│  └───────────────┘   - AI metrics                         │
│                      - Business metrics                    │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## 10. Key Architectural Decisions

### ADR-001: Event-Driven AI Processing

**Decision:** Use event-driven architecture for AI processing

**Rationale:**
- Decouples AI processing from user requests
- Allows async processing of AI tasks
- Enables better scalability
- Supports retry and error handling

**Consequences:**
- ✅ Better user experience (no blocking)
- ✅ Better resource utilization
- ✅ Easier to add new AI agents
- ❌ Added complexity in event handling
- ❌ Need for event ordering guarantees

### ADR-002: LLM Gateway Pattern

**Decision:** Use LLM Gateway to abstract LLM provider

**Rationale:**
- Easy to switch between providers
- Centralized retry, logging, and monitoring
- Consistent interface for all agents

**Consequences:**
- ✅ Provider agnostic code
- ✅ Easy to add new providers
- ✅ Centralized cost tracking
- ❌ Additional abstraction layer

### ADR-003: Repository Pattern

**Decision:** Use Repository pattern for data access

**Rationale:**
- Clean separation between business logic and data access
- Easy to mock for testing
- Can change data source without changing business logic

**Consequences:**
- ✅ Testable code
- ✅ Flexible data layer
- ✅ Clean architecture
- ❌ More code to maintain

---

*Document Version: 1.0*  
*Last Updated: 2026-08-13*
