# MemoryChat AI Agent Instructions (AGENTS.md)

This document defines the strict rules that all AI coding agents (Everything Claude Code - ECC) must follow when modifying the MemoryChat repository. 

**These rules reflect the CURRENT state of the repository, not idealized architectures or future plans.**

---

## 1. Project Identity & Tech Stack
MemoryChat is an AI-powered P2P messaging platform with background memory extraction and semantic search capabilities.

**Current Tech Stack:**
- **Backend:** FastAPI (Python), SQLAlchemy 2.0 (PostgreSQL/SQLite), Alembic.
- **Frontend:** Next.js 15 (React 19), TailwindCSS, Zustand (client state), `@tanstack/react-query` (server state).
- **AI/Vector DB:** OpenAI (`gpt-4o-mini`), LangChain (`bind_tools`), ChromaDB.
- **Testing:** Pytest (Backend), Playwright (E2E Frontend).

## 2. Core Architecture Rules

### 2.1 WebSockets & Real-time Sync
- **Unidirectional Flow:** The WebSocket connection (`src/api/ws.py`) is used strictly for **server-to-client** push events. Clients MUST use standard REST API `POST` requests to send messages or trigger actions.
- **State Synchronization:** The frontend `ws-bootstrap.tsx` listens to WS events (e.g., `NEW_MESSAGE`, `MESSAGE_RECALLED`) and directly mutates the `@tanstack/react-query` cache. Do not trigger full network refetches on every WS event.
- **No Redis:** The `ConnectionManager` is currently an **in-memory** structure. Do not assume or implement Redis Pub/Sub unless specifically instructed to design horizontal scaling.

### 2.2 EventBus & Outbox Pattern
- **Background Tasks:** Actions that require heavy processing (like AI memory extraction) MUST NOT block REST endpoints. 
- **Outbox Pattern:** Publish events to the `EventBus` via the `outbox_events` table within the same SQLAlchemy transaction as the domain entity changes. `OutboxWorker` handles reliable delivery.

### 2.3 AI Architecture (LangChain, NOT LangGraph)
- **Tool Calling:** The Copilot orchestrator (`src/agents/orchestrator.py`) uses LangChain's standard `bind_tools` logic. It implements a `DummyGraph` internally for backward compatibility. 
- **DO NOT** attempt to write or debug LangGraph state machines for the core Copilot logic.
- **Background Extraction:** The `MemoryWorker` extracts facts/summaries asynchronously and pushes to ChromaDB.

## 3. Non-Negotiable Invariants

1. **Authorization:** Any mutable action on a User, Message, or Conversation MUST verify that the requesting `user_id` matches the owner of the resource (e.g., returning `403 Forbidden`).
2. **Soft Deletion:** Messages are NEVER hard-deleted. They must be soft-deleted using the `deleted_at` timestamp.
3. **ORM Mutation Allowed:** Unlike generic ECC rules, SQLAlchemy ORM object mutation is the standard pattern in this backend. Do not force strict immutability on SQLAlchemy models.
4. **P2P Only:** The database schema (`user_a_id`, `user_b_id`) is strictly designed for P2P (Direct) conversations. Do not attempt to implement Group Chat logic without a major schema migration.
5. **No AI Blocking:** Core chat functionality (sending/receiving messages) must remain fully functional even if the AI or ChromaDB fails.

## 4. Coding Conventions

- **Frontend API Calls:** Keep API client logic in `frontend/lib/api/` and wrap them with `useQuery` or `useMutation` from React Query inside components.
- **Backend Services:** Business logic belongs in `src/services/`. FastAPI routers (`src/api/v1/`) should solely handle HTTP validation and response formatting. Controllers must not perform direct database commits; they delegate to services.
- **Secrets:** Never hardcode secrets. Use environment variables defined in `.env.example` and parsed via `src.config`.

## 5. Testing Rules

- **Coverage:** TDD is recommended for critical business logic (e.g., message deletion, authorization, AI tool extraction). Do not force meaningless tests just to satisfy coverage percentages.
- **Current State:** Note that the `pytest` suite is currently unstable due to legacy imports (`No module named 'src.repositories.contact'`). Agents should not delete failing tests just to make the suite pass; fix the imports or bypass safely if unrelated to the current task.

## 6. AI Development Workflow & ECC Agents

When working on this repository, follow this flow:
`Inspect -> Understand -> Plan -> Implement -> Test -> Review -> Verify`

**Recommended ECC Agents to Invoke:**
- `planner`: For complex features (e.g., migrating to Cursor-based pagination).
- `python-reviewer` / `typescript-reviewer`: After significant code changes.
- `database-reviewer`: For any Alembic schema changes.
- `build-error-resolver`: When Next.js typecheck or Pytest fails.

## 7. Protection From AI Drift

Agents MUST NOT:
- Create duplicate WebSocket managers or Event mechanisms. Reuse the existing `wsManager` and `EventBus`.
- Introduce new architectural patterns (e.g., Repository Pattern) unless explicitly requested. The current backend mixes Services and raw SQLAlchemy queries.
- Expose sensitive API keys in the chat UI or logs.
- Modify documentation to reflect idealized future architectures. Documentation must match the running code.

*If an explicit architectural change is required, the Agent must first propose the change and wait for user approval.*

# MemoryChat Agent Operating Instructions

You are working on the **MemoryChat** repository.

Before doing any implementation, establish the project's documentation hierarchy and understand how each document must be used.

> **IMPORTANT:** Do not blindly copy or apply generic Everything Claude Code (ECC) rules to MemoryChat. ECC is the AI tooling/workflow layer; the repository documentation defines MemoryChat-specific rules, architecture, decisions, and product direction.

---

## 1. Inspect Before Working

First inspect the repository and read the existing documentation:

- `README.md`
- `AGENTS.md`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- `long-term.md`
- `WORKLOG.md`
- `JOURNAL.md`

Then inspect the actual source code, tests, migrations, configuration, frontend, backend, WebSocket, authentication/authorization, and AI/RAG implementation relevant to the task.

Never assume documentation is more accurate than the actual implementation.

---

## 2. Documentation Hierarchy

Each document has a specific responsibility.

### `AGENTS.md`

Defines **HOW AI agents must work in this repository**.

Use it for:

- Coding rules
- Security rules
- Testing policy
- Architectural constraints
- ECC integration
- Development workflow
- Prohibited behaviors

It is the primary project-specific instruction file for AI agents.

---

### `ARCHITECTURE.md`

Describes **HOW THE CURRENT SYSTEM ACTUALLY WORKS**.

Use it to understand:

- System architecture
- Frontend architecture
- Backend architecture
- Database architecture
- Authentication
- Authorization
- Conversations
- Messages
- WebSockets
- AI/RAG
- Data flows
- Component relationships

It must describe the current implementation, not an idealized future architecture.

---

### `DECISIONS.md`

Records **WHY important architectural and product decisions were made**.

Use it to understand:

- Accepted architectural decisions
- Product decisions
- Reasoning
- Trade-offs
- Rejected alternatives
- Important constraints created by previous decisions

Do not treat assumptions or future proposals as accepted decisions.

---

### `long-term.md`

Describes **WHERE MEMORYCHAT IS GOING**.

Use it to understand:

- Product vision
- Long-term engineering direction
- Stable principles
- Future goals
- Non-goals
- Future architectural direction

Future plans must never automatically be treated as currently implemented features.

---

### `WORKLOG.md`

Tracks **WHAT HAS BEEN DONE**.

Use it to understand:

- Completed work
- Current work
- Remaining tasks
- Blockers
- Implementation progress

Do not treat unfinished tasks as implemented features.

---

### `JOURNAL.md`

Records **WHAT WAS LEARNED** during development.

Use it for:

- Engineering discoveries
- Debugging findings
- Root causes
- Lessons learned
- Historical implementation context

Do not treat journal observations as architectural decisions unless they are also recorded in `DECISIONS.md`.

---

## 3. ECC Integration

MemoryChat uses **Everything Claude Code (ECC)** as its AI development tooling and workflow layer.

ECC provides:

- Specialized agents
- Skills
- Commands
- Hooks
- Development workflows

Use appropriate ECC agents when useful:

| Agent | Use When |
|---|---|
| `planner` | Complex features/refactors |
| `architect` | Architectural decisions |
| `tdd-guide` | Business logic/features/bug fixes |
| `code-reviewer` | After implementation |
| `security-reviewer` | Security-sensitive changes |
| `e2e-runner` | Critical user flows |
| `database-reviewer` | Schema/query/migration changes |
| `python-reviewer` | Backend Python changes |
| `typescript-reviewer` | Frontend TypeScript/JavaScript |
| `rag-pipeline-reviewer` | RAG/vector retrieval changes |
| `build-error-resolver` | Build/type errors |

ECC recommendations must not override:

- MemoryChat architecture
- Accepted project decisions
- Security boundaries
- Product requirements
- Explicit rules in this repository

ECC provides the **tools and workflow**.

MemoryChat documentation provides the **project-specific context and constraints**.

---

## 4. Standard Development Workflow

For every task:

```text
Inspect
  ↓
Understand
  ↓
Plan
  ↓
Implement
  ↓
Test
  ↓
Review
  ↓
Verify
  ↓
Update Documentation
  ↓
Report