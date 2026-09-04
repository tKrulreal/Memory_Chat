# Architecture Diagram — MemoryChat

## 1. System Overview

```mermaid
graph TB
    subgraph Frontend["🌐 Frontend (Next.js 14)"]
        UI[Web App<br/>React Components]
        State[State Management<br/>Zustand + TanStack Query]
    end

    subgraph Backend["⚙️ Backend (FastAPI)"]
        API[REST API]
        WS[WebSocket Server]
        Agents[AI Agents<br/>LangGraph]
        Workers[Background Workers<br/>Outbox, Memory]
    end

    subgraph DataLayer["💾 Data Layer"]
        PG[(PostgreSQL<br/>15)]
        Qdrant[(Qdrant Cloud<br/>Vector DB)]
        Cache[Redis<br/>Optional Cache]
    end

    subgraph External["🔌 External Services"]
        LLM[OpenAI /<br/>OpenRouter]
        LangSmith[LangSmith<br/>Tracing]
    end

    User([👤 User]) --> UI
    UI --> State
    UI --> API
    UI --> WS
    API --> Agents
    WS --> Agents
    Agents --> LLM
    Agents --> Tools[Agent Tools]
    Tools --> PG
    Agents --> Qdrant
    API --> PG
    Workers --> PG
    Workers --> Qdrant
    Agents --> LangSmith
```

---

## 2. Multi-Agent Architecture

```mermaid
graph TB
    subgraph Orchestrator["🎯 Orchestrator Agent"]
        Router[Query Router]
        Intent[Intent Detection]
    end

    subgraph Specialized["🔧 Specialized Agents"]
        Memory[Memory Agent<br/>- Extract facts<br/>- Summarize<br/>- Search memories]
        Copilot[Copilot Agent<br/>- Chat with context<br/>- Relationship-aware]
        Matchmaker[Matchmaker Agent<br/>- Jaccard similarity<br/>- Mutual goals<br/>- Geography]
        Reply[Reply Suggestion<br/>- Context analysis<br/>- Tone matching]
        Search[Search Agent<br/>- Semantic search<br/>- Keyword search]
    end

    Router --> Intent
    Intent -->|Memory| Memory
    Intent -->|Copilot| Copilot
    Intent -->|Match| Matchmaker
    Intent -->|Reply| Reply
    Intent -->|Search| Search
```

---

## 3. Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as FastAPI
    participant WS as WebSocket
    participant Agent as LangGraph
    participant LLM as OpenAI
    participant PG as PostgreSQL
    participant Qdr as Qdrant

    U->>F: Send message
    F->>API: POST /messages
    API->>PG: Store message
    PG-->>API: Message saved
    API->>WS: Broadcast event
    WS->>F: Real-time delivery
    
    Note over U,PG: Optional AI Processing
    
    U->>F: Ask Copilot
    F->>API: POST /copilot/chat
    API->>Agent: Process query
    Agent->>LLM: Generate response
    Agent->>PG: Check context
    Agent->>Qdr: Semantic search
    Qdr-->>Agent: Relevant memories
    Agent-->>LLM: Contextual response
    LLM-->>Agent: Response
    Agent-->>API: Final response
    API-->>F: Display response
```

---

## 4. Component Details

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS | User interface |
| **State** | Zustand, TanStack Query | Client state management |
| **Backend API** | FastAPI, Python 3.11, SQLAlchemy 2.0 | REST endpoints |
| **WebSocket** | FastAPI WebSocket, python-socketio | Real-time messaging |
| **Orchestrator** | LangGraph | Multi-agent coordination |
| **LLM Gateway** | LangChain, OpenAI, OpenRouter | AI inference |
| **Vector Store** | Qdrant Cloud | Semantic memory storage |
| **Database** | PostgreSQL 15, Alembic | Relational data |
| **Workers** | asyncio Background Tasks | Async processing |

---

## 5. Database Schema Overview

```mermaid
erDiagram
    USER ||--o{ CONVERSATION : has
    USER ||--o{ MESSAGE : sends
    USER ||--o{ CONNECTION : requests
    USER ||--o{ AI_MEMORY : stores
    USER ||--o{ COPILOT_MESSAGE : chats
    CONVERSATION ||--o{ MESSAGE : contains
    USER ||--o{ NOTIFICATION : receives

    USER {
        uuid id PK
        string email
        string password_hash
        string full_name
        jsonb profile_data
        datetime created_at
    }

    CONVERSATION {
        uuid id PK
        uuid user1_id FK
        uuid user2_id FK
        datetime created_at
    }

    MESSAGE {
        uuid id PK
        uuid conversation_id FK
        uuid sender_id FK
        text content
        datetime created_at
        datetime deleted_at
    }

    AI_MEMORY {
        uuid id PK
        uuid user_id FK
        text content
        vector embedding
        string memory_type
        datetime created_at
    }
```

---

## 6. Deployment Architecture

```mermaid
graph LR
    subgraph Production["☁️ Production (Railway)"]
        Frontend[Frontend<br/>Vercel/Static]
        Backend[Backend<br/>Railway]
        DB[(PostgreSQL<br/>Railway Postgres)]
        Vector[(Qdrant Cloud)]
    end

    subgraph DevOps["🔄 CI/CD (GitHub Actions)"]
        CI[CI Pipeline]
        CD[CD Pipeline]
    end

    CI -->|Test| Backend
    CD -->|Deploy| Frontend
    CD -->|Deploy| Backend
```

---

## 7. Security Architecture

```mermaid
graph TB
    subgraph Security["🔒 Security Layer"]
        RateLimit[Rate Limiting<br/>100 req/min]
        Auth[JWT Auth<br/>Access + Refresh]
        CORS[CORS Policy]
        InputVal[Input Validation<br/>Pydantic]
    end

    User --> RateLimit
    RateLimit --> Auth
    Auth --> CORS
    CORS --> InputVal
    InputVal --> API[API Handler]
```

---

## 8. Key Files Reference

| File | Description |
|------|-------------|
| `src/main.py` | FastAPI application entry point |
| `src/agents/` | LangGraph agent definitions |
| `src/api/` | REST API routers |
| `src/models/` | SQLAlchemy database models |
| `src/services/` | Business logic services |
| `src/core/` | Security, config, middleware |
| `alembic/versions/` | Database migrations |
| `tests/` | Test suite |
