# MemoryChat — AI-Powered P2P Messaging Platform

## 1. What MemoryChat Is
MemoryChat is a real-time messaging platform enhanced by an AI Copilot. It continuously analyzes conversations in the background to extract relationship insights, build contact profiles, and provide contextual recommendations to users.

## 2. Core Product Concept
The core concept is an "Intelligent Inbox." As users chat, background workers securely read the messages, summarize them, extract factual data (skills, interests, professional backgrounds), and store them in a vector database. Users can then ask the AI Copilot natural language questions to search through their chat history or get smart reply suggestions.

## 3. Main Features Currently Implemented
- **Direct P2P Chat:** Real-time messaging using WebSockets.
- **Message Lifecycle:** Send and Recall (soft delete) messages.
- **AI Memory Extraction:** Background workers analyze conversations after 5 minutes of inactivity to extract facts.
- **Copilot Semantic Search:** AI assistant capable of finding contacts based on chat history or public profile skills.
- **Smart Recommendations:** The AI suggests follow-ups, replies, and connection opportunities.
- **Connection Management:** Users can send, accept, and reject connection requests.

## 4. Current Tech Stack
- **Backend:** FastAPI (Python), SQLAlchemy 2.0 (PostgreSQL/SQLite)
- **Frontend:** Next.js 15 (React 19), TailwindCSS, Zustand, React Query
- **AI/LLM:** OpenAI (`gpt-4o-mini`) via LangChain tools (not LangGraph as previously documented)
- **Vector Database:** ChromaDB
- **Event Management:** In-memory EventBus + Transactional Outbox pattern
- **Testing:** Pytest (Backend), Playwright (E2E Frontend)

## 5. High-Level Architecture
MemoryChat is built as a monolithic FastAPI backend serving a Next.js SPA frontend. 
1. **REST API**: Handles standard CRUD (auth, fetch messages, profiles).
2. **WebSocket Server**: Provides unidirectional (server-to-client) real-time events.
3. **Event Bus & Outbox**: Guarantees background processing (memory extraction, notifications) executes reliably after DB commits.
4. **Agent Layer**: LLM integrations hooked into the Event Bus (background) and Copilot endpoints (synchronous).

## 6. Repository Structure
```
├── alembic/              # Database schema migrations
├── src/                  # FastAPI Backend Core
│   ├── agents/          # Copilot AI tools, Search, and Memory extraction logic
│   ├── api/v1/          # REST endpoints
│   ├── models/          # SQLAlchemy DB models
│   ├── services/        # Business logic controllers
│   ├── workers/         # Background tasks (Outbox, Memory, Connection)
│   └── ws/              # WebSocket manager
├── frontend/             # Next.js Application
│   ├── app/             # App router pages
│   ├── components/      # React components (Chat, Layout, AI UI)
│   ├── lib/             # API clients, Stores (Zustand), WebSocket handlers
│   └── package.json     # Node dependencies
├── tests/                # Backend Pytest suite
└── docker-compose.yml    # Local infrastructure deployment
```

## 7. How to Configure the Development Environment
1. Clone the repository.
2. Install Python >= 3.11 for the backend.
3. Install Node.js >= 20 for the frontend.
4. Create the necessary environment configuration (see below).
5. Install backend dependencies: `pip install -r requirements.txt` (or via Make).
6. Install frontend dependencies: `cd frontend && npm install`.

## 8. Required Environment Variables
Copy `.env.example` to `.env` in the root directory. You must supply:
- `OPENAI_API_KEY`: A valid OpenAI API key for embeddings and Copilot generation.
- `DATABASE_URL`: Connection string for PostgreSQL or SQLite (e.g., `sqlite:///./memorychat.db`).
- `JWT_SECRET`: A secure random string for signing JWT tokens.

*Note: Never commit your `.env` file or expose these secrets.*

## 9. How to Run Backend and Frontend
**Using Make/Docker (Recommended):**
```bash
make setup
make run
```
*This starts the FastAPI backend on port 8000.*

**Starting Frontend (Separate Terminal):**
```bash
cd frontend
npm run dev
```
*This starts the Next.js app on port 3000.*

## 10. How to Run Tests & Quality Checks
**Backend Tests:**
```bash
pytest tests/ -v
```

**Frontend Checks:**
```bash
cd frontend
npm run lint       # Run ESLint
npm run typecheck  # Run TypeScript compiler checks
```

**E2E Tests (Playwright):**
```bash
cd frontend
npx playwright install
npx playwright test
```

## 11. Database Migration Commands
The project uses Alembic for database schema management.
- Run pending migrations: `alembic upgrade head`
- Generate new migration (after modifying models): `alembic revision --autogenerate -m "description"`
- Rollback one step: `alembic downgrade -1`

## 12. WebSocket Architecture
- **Unidirectional Flow:** The WebSocket connection (`GET /ws/chat`) is used strictly for server-to-client push events. Clients must use standard REST API `POST` requests to send messages or trigger actions.
- **In-Memory Manager:** Currently, `ConnectionManager` holds active connections in RAM. This means the backend currently cannot be horizontally scaled without introducing a Redis Pub/Sub backplane.
- **React Query Integration:** The frontend `ws-bootstrap.tsx` component listens to WS events and directly mutates the `@tanstack/react-query` cache (e.g., adding messages or marking them as deleted) to provide a snappy UI without refetching data.

## 13. AI/RAG Components
- **Background Memory Extraction:** When a chat goes idle for > 5 minutes, `MemoryWorker` invokes `MemoryAgent` to summarize the conversation and extract factual data, saving it into `AssistantMemory`.
- **Vector Ingestion (ChromaDB):** The extracted memory is vectorized via OpenAI embeddings and stored in a local ChromaDB instance to enable semantic search.
- **Copilot (LangChain):** The `/api/v1/copilot` endpoint uses an orchestrator built with LangChain `bind_tools`. It can dynamically search ChromaDB, retrieve recent messages, and read peer profiles to answer user queries contextually.

## 14. Current Production / Deployment Status
- **Status:** MVP / Development phase.
- **Deployment Strategy:** `docker-compose.yml` provides a unified local deployment containing the Uvicorn server. For production, the Next.js app requires standard Node.js hosting (e.g., Vercel, PM2), and the backend requires a proper PostgreSQL instance.
- **Horizontal Scaling Limits:** Currently limited to a single backend container due to local ChromaDB and in-memory WebSocket/EventBus implementations.

## 15. Important Development Notes
- **Message Soft-Deletion:** Messages cannot be hard-deleted. Always use `deleted_at` (e.g., the Message Recall feature).
- **Outbox Pattern:** When adding new features that trigger side-effects (like notifications or AI processing), never call the workers synchronously. Always emit an `OutboxEvent` inside the SQLAlchemy transaction block to guarantee execution.
- **API Boundaries:** Business logic belongs in `src/services/`, not in the FastAPI routers (`src/api/v1/`). Routers should solely handle HTTP validation and response formatting.
