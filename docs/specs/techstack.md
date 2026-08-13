# TECHSTACK.md — Technology Stack

## MemoryChat MVP v1.0

---

## 1. Technology Stack Overview

### 1.1 Stack at a Glance

| Layer | MVP Technology | Future (Post-MVP) |
|-------|---------------|-------------------|
| **API Framework** | FastAPI + Uvicorn | FastAPI + Gunicorn |
| **LLM Framework** | LangGraph + LangChain | LangGraph + LangChain |
| **LLM Provider** | OpenAI (gpt-4o-mini) | Multi-provider |
| **Database** | SQLite (via SQLAlchemy) | PostgreSQL |
| **Vector DB** | ChromaDB | Qdrant |
| **Graph DB** | — | Neo4j |
| **Cache** | In-memory | Redis |
| **Frontend** | — | React + TypeScript |
| **Mobile** | — | Flutter |
| **Container** | Docker (single) | Docker Compose |
| **Background Job** | asyncio tasks | Celery + Redis |

---

## 2. Backend Stack

### 2.1 API Framework

```
FastAPI + Uvicorn
```

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| Framework | FastAPI | Async-first, auto Swagger docs |
| Server | Uvicorn | ASGI server, async native |
| Validation | Pydantic v2 | Type safety, auto docs |
| Settings | Pydantic Settings | .env integration |
| ORM | SQLAlchemy 2.0 | Async ORM support |

**Why FastAPI?**
- Native async support
- Automatic OpenAPI documentation
- Type safety with Pydantic
- Easy integration with LangChain/LangGraph
- Active community and fast development

**Why not Flask?**
- Synchronous by default
- Requires more boilerplate
- Less modern tooling

### 2.2 AI Framework

```
LangGraph + LangChain
```

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| Orchestration | LangGraph | Multi-agent, state management |
| LLM Integration | LangChain | Standard abstractions |
| Tool Calling | LangChain Tools | MCP-ready |
| Memory | LangGraph Checkpointer | State persistence |

**Why LangGraph?**
- Designed for multi-agent workflows
- Built-in state management
- Human-in-the-loop support
- Easy branching and parallel execution
- LangSmith integration for observability

### 2.3 LLM Provider

```
OpenAI (gpt-4o-mini)
```

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| Primary Model | gpt-4o-mini | Cost-effective, fast |
| Embedding | text-embedding-3-small | Efficient |
| Fallback | gpt-4o | Complex tasks |

**Why gpt-4o-mini?**
- 60x cheaper than gpt-4
- Fast response times
- Sufficient for memory/search tasks
- Easy to upgrade to gpt-4o when needed

**Future Providers:**
- Anthropic Claude (complex reasoning)
- Google Gemini (multimodal)
- Local LLM via Ollama/vLLM (privacy, cost)

---

## 3. Database Stack

### 3.1 Transactional Database

```
MVP: SQLite → Post-MVP: PostgreSQL
```

| Aspect | MVP | Post-MVP |
|--------|-----|----------|
| Engine | SQLite | PostgreSQL 15+ |
| ORM | SQLAlchemy 2.0 | SQLAlchemy 2.0 |
| Migration | Manual | Alembic |
| Pooling | N/A (single file) | PgBouncer |

**Why SQLite for MVP?**
- Zero setup required
- File-based persistence
- Good for development/demo
- Easy migration to PostgreSQL via ORM

**Why PostgreSQL Post-MVP?**
- Better concurrency
- JSON support
- Full-text search
- Replication support

### 3.2 Vector Database

```
MVP: ChromaDB → Post-MVP: Qdrant
```

| Aspect | MVP | Post-MVP |
|--------|-----|----------|
| Engine | ChromaDB | Qdrant |
| Index | HNSW | HNSW |
| Similarity | Cosine | Cosine |
| Deployment | Embedded | Docker Cluster |

**Why ChromaDB for MVP?**
- Pure Python, no external service
- Easy to run locally
- Simple API
- Good for prototyping

**Why Qdrant Post-MVP?**
- Production-grade
- Better performance
- Filtering support
- Cloud offering available

### 3.3 Graph Database

```
Post-MVP: Neo4j
```

| Node Types | Edge Types |
|------------|------------|
| User | KNOW |
| Contact | WORK_AT |
| Company | INTEREST_IN |
| Skill | HAS_SKILL |
| Topic | LOCATED_IN |
| Interest | TALKED_ABOUT |

**Why Neo4j?**
- Native graph queries
- Cypher language
- Relationship traversal
- ACID compliance

### 3.4 Cache Layer

```
MVP: In-Memory → Post-MVP: Redis
```

| Cache Type | MVP | Post-MVP |
|------------|-----|----------|
| Context | In-memory dict | Redis |
| Session | JWT only | Redis Session |
| LLM Cache | File-based | Redis |
| Rate Limit | N/A | Redis |

**Why Redis Post-MVP?**
- Sub-millisecond latency
- Pub/sub for real-time
- Sorted sets for rankings
- TTL support

---

## 4. Frontend Stack

### 4.1 Web Application

```
React + TypeScript + Vite
```

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| Framework | React 18 | Ecosystem, team familiarity |
| Language | TypeScript | Type safety |
| Build | Vite | Fast HMR, modern |
| Routing | React Router v6 | Standard |
| State | Zustand | Lightweight, simple |
| Styling | TailwindCSS | Rapid development |
| Animation | Framer Motion | Smooth animations |
| Forms | React Hook Form | Performance |
| API Client | TanStack Query | Caching, refetch |

**Why React?**
- Largest ecosystem
- Team familiarity
- Strong TypeScript support
- Good AI/LLM integration options

### 4.2 Mobile Application

```
Flutter (Future)
```

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| Framework | Flutter 3+ | Cross-platform |
| Language | Dart | Flutter native |
| State | Riverpod | Compile-safe |
| Navigation | GoRouter | Declarative |

---

## 5. Infrastructure Stack

### 5.1 Container & Orchestration

```
MVP: Docker Single Container → Post-MVP: Docker Compose / Kubernetes
```

| Component | MVP | Post-MVP |
|-----------|-----|----------|
| Container | Docker | Docker Compose |
| Registry | Docker Hub | ECR/GCR |
| Orchestration | — | Kubernetes (future) |
| CI/CD | Manual | GitHub Actions |

### 5.2 Monitoring & Logging

```
MVP: Application Logs → Post-MVP: Prometheus + Grafana
```

| Aspect | MVP | Post-MVP |
|--------|-----|----------|
| Logs | stdout + file | ELK Stack |
| Metrics | Application | Prometheus |
| Dashboards | — | Grafana |
| Tracing | — | OpenTelemetry |
| APM | — | LangSmith |

### 5.3 Security

```
MVP: Basic → Post-MVP: Full Security Stack
```

| Aspect | MVP | Post-MVP |
|--------|-----|----------|
| Auth | — | JWT + Refresh Token |
| Password | — | BCrypt |
| HTTPS | Reverse Proxy | Automatic |
| Rate Limit | — | Redis-based |
| CORS | Configured | Strict |
| SQL Injection | ORM | ORM + validation |
| XSS | — | Sanitization |
| Prompt Injection | Basic | Advanced Detection |

---

## 6. Development Tools

### 6.1 IDE & Extensions

| Tool | Purpose |
|------|---------|
| VS Code | Primary IDE |
| Python Extension | Python development |
| Pylance | Type checking |
| ESLint | JS/TS linting |
| Prettier | Code formatting |
| Docker Extension | Container management |

### 6.2 Testing

| Type | Tool | Coverage |
|------|------|----------|
| Unit | pytest | Core logic |
| Integration | FastAPI TestClient | API endpoints |
| E2E | Playwright | User flows |
| AI Testing | Manual + Structured | Prompts, outputs |

### 6.3 Documentation

| Type | Tool |
|------|------|
| Code Docs | docstrings, type hints |
| API Docs | OpenAPI/Swagger (auto) |
| Architecture | Mermaid diagrams |
| Specs | Markdown files |

---

## 7. Environment Variables

### 7.1 Required Variables

```env
# OpenAI
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4o-mini

# Database
DATABASE_URL=sqlite:///./data/app.db

# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma

# App
LOG_LEVEL=INFO
ENVIRONMENT=development

# JWT (Post-MVP)
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 7.2 Optional Variables

```env
# Redis (Post-MVP)
REDIS_URL=redis://localhost:6379

# PostgreSQL (Post-MVP)
POSTGRES_USER=memorychat
POSTGRES_PASSWORD=password
POSTGRES_DB=memorychat
POSTGRES_HOST=localhost

# Neo4j (Post-MVP)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

---

## 8. Cost Estimation (MVP)

### 8.1 Infrastructure Costs

| Service | MVP Cost | Post-MVP Cost |
|---------|----------|---------------|
| Compute | $0 (local) | ~$20-50/month |
| Database | $0 | ~$10-20/month |
| Vector DB | $0 | ~$10-30/month |
| LLM API | ~$1-10/month | ~$20-100/month |
| Monitoring | $0 | ~$10-20/month |
| **Total** | **$1-10/month** | **$50-220/month** |

### 8.2 LLM Cost Breakdown

| Task | Model | Input | Output | Est. Monthly |
|------|-------|-------|--------|--------------|
| Memory Summary | gpt-4o-mini | 1K | 500 | ~$0.50 |
| Search | gpt-4o-mini | 500 | 200 | ~$0.20 |
| Recommendation | gpt-4o-mini | 2K | 500 | ~$0.30 |
| Copilot | gpt-4o | 4K | 1K | ~$2.00 |

---

## 9. Migration Path

### 9.1 MVP → Phase 2

```
SQLite → PostgreSQL
ChromaDB → Qdrant
In-memory → Redis
asyncio → Celery
Single container → Docker Compose
```

### 9.2 Phase 2 → Phase 3

```
Add Neo4j for Knowledge Graph
Add MCP Server for external integrations
Add Multi-LLM routing
Consider local LLM for privacy
```

### 9.3 Phase 3 → Phase 4

```
Kubernetes deployment
Multi-region setup
Enterprise features
Advanced analytics
```

---

## 10. Technology Decision Records

### ADR-001: Use LangGraph for Agent Orchestration

**Context:** Multi-agent system with complex workflows

**Decision:** Use LangGraph

**Consequences:**
- ✅ Built-in state management
- ✅ Human-in-the-loop support
- ✅ Easy branching
- ✅ LangSmith integration
- ❌ Learning curve
- ❌ Vendor lock-in potential

### ADR-002: Use SQLite for MVP Database

**Context:** Quick development, demo focus

**Decision:** Use SQLite

**Consequences:**
- ✅ Zero setup
- ✅ Easy development
- ✅ ORM abstraction allows migration
- ❌ Limited concurrency
- ❌ Not suitable for production

### ADR-003: Use gpt-4o-mini as Primary Model

**Context:** Cost-sensitive MVP

**Decision:** Use gpt-4o-mini

**Consequences:**
- ✅ 60x cheaper than gpt-4
- ✅ Fast responses
- ✅ Sufficient quality
- ❌ May need upgrade for complex tasks

### ADR-004: Use ChromaDB for Vector Search

**Context:** MVP, local development

**Decision:** Use ChromaDB

**Consequences:**
- ✅ No external service
- ✅ Easy setup
- ✅ Good for prototyping
- ❌ Not production-grade
- ❌ Limited filtering

---

## 11. Dependencies

### 11.1 Python Dependencies

```txt
# Core
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# Database
sqlalchemy>=2.0.25
aiosqlite>=0.19.0

# AI
langgraph>=0.0.20
langchain>=0.1.0
langchain-openai>=0.0.5

# Vector DB
chromadb>=0.4.22

# Utils
python-dotenv>=1.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# Testing
pytest>=7.4.0
pytest-asyncio>=0.23.0
httpx>=0.26.0
```

### 11.2 Frontend Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "zustand": "^4.4.0",
    "tailwindcss": "^3.4.0",
    "framer-motion": "^10.18.0",
    "@tanstack/react-query": "^5.17.0",
    "react-hook-form": "^7.49.0",
    "axios": "^1.6.0",
    "lucide-react": "^0.303.0"
  }
}
```

---

## 12. Browser Support

| Browser | Minimum Version |
|---------|----------------|
| Chrome | 90+ |
| Firefox | 90+ |
| Safari | 14+ |
| Edge | 90+ |

---

*Document Version: 1.0*  
*Last Updated: 2026-08-13*
