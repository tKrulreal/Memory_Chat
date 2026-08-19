# MemoryChat — Pre-Deployment Implementation Plan

> **Goal:** Prepare MemoryChat for the first production deployment of the Web application while keeping the backend/API/WebSocket architecture ready for the future mobile application.
>
> **Scope:** This document covers the **Pre-Deployment phase only**. Do not prematurely implement horizontal scaling, Kubernetes, Redis WebSocket Pub/Sub, semantic caching, or other scale-only infrastructure unless the current deployment architecture actually requires it.

---

# 1. Objective

Before the first production deployment, MemoryChat must be:

- Reliable enough for real users.
- Secure enough for production.
- Observable when something fails.
- Testable and protected against regressions.
- Efficient for normal chat workloads.
- Correct under WebSocket disconnect/reconnect scenarios.
- Ready for Web and future Mobile clients to share the same API/WebSocket contract.
- Safe to deploy and rollback.

The core principle is:

> **Make the current system correct, predictable, observable, and deployable before optimizing for large-scale traffic.**

---

# 2. Current Architecture Baseline

The current application should continue following the existing architecture:

```text
Next.js / React Frontend
        │
        ├── REST API
        └── WebSocket
                │
                ▼
          FastAPI Backend
                │
        ┌───────┴────────┐
        │                │
     Services          WebSocket
        │               Manager
        │
        ▼
    PostgreSQL
        │
        └───────────────┐
                        │
                  AI / RAG Layer
                        │
                 ChromaDB + LLM
```

The backend remains the source of truth for:

- Users
- Connections
- Connection Requests
- Conversations
- Messages
- Message state
- Authentication/authorization

AI and vector search must remain separated from the transactional chat path.

---

# 3. Priority Levels

Use the following priorities:

### P0 — Must be completed before production

A failure here can cause data loss, security problems, broken core functionality, or an unsafe deployment.

### P1 — Strongly recommended before production

Important for reliability and maintainability, but not necessarily a blocker for the first small-scale deployment.

### P2 — Post-deployment / scale optimization

Do not implement before deployment unless real requirements justify it.

---

# 4. Phase 0 — Repository and Architecture Baseline

## Priority: P0

Before implementing infrastructure changes, inspect the current codebase.

Read and respect:

```text
README.md
AGENTS.md
ARCHITECTURE.md
JOURNAL.md
WORKLOG.md
long-term.md
```

Then inspect:

```text
backend
frontend
database migrations
tests
deployment configuration
environment configuration
WebSocket implementation
AI workers/agents
```

### Requirements

- Do not create duplicate architecture.
- Reuse existing services and abstractions.
- Do not rewrite stable features unnecessarily.
- Record significant architecture decisions in the existing decision/documentation workflow.
- Keep `ARCHITECTURE.md`, `JOURNAL.md`, and `WORKLOG.md` synchronized with important changes.

### Definition of Done

- [ ] Existing architecture is understood.
- [ ] Current test commands are known.
- [ ] Current build commands are known.
- [ ] Current migration process is known.
- [ ] Current environment variables are documented.
- [ ] Existing deployment assumptions are documented.

---

# 5. Phase 1 — Fix and Stabilize Test Suite

## Priority: P0

The project must not enter production with a broken baseline test suite.

## Backend

Run:

```bash
pytest
```

Fix all existing import/module failures and broken tests.

Previously observed examples include missing modules such as:

```text
src.repositories.contact
src.agents.insight
```

Do not simply skip or delete failing tests.

Determine whether each failure is:

1. A stale test.
2. A missing implementation.
3. An outdated import.
4. An actual regression.

Update tests to match the current P2P architecture.

## Frontend

Run:

```bash
npm run lint
npm run typecheck
```

Fix all errors.

## E2E

Inspect the existing Playwright configuration.

Run the existing E2E suite if available.

### Minimum critical flows

```text
Login
  ↓
Open conversation
  ↓
Send message
  ↓
Receive message
  ↓
Recall message
  ↓
Connection Request
  ↓
Accept connection
  ↓
Conversation available
```

### Definition of Done

- [ ] Backend tests pass.
- [ ] Frontend lint passes.
- [ ] Frontend typecheck passes.
- [ ] Existing E2E tests pass.
- [ ] No failures are hidden by disabling/skipping tests without documented justification.

---

# 6. Phase 2 — Database Production Readiness

## Priority: P0

PostgreSQL is the source of truth.

## 6.1 Migration integrity

Verify:

```text
Development DB
      ↓
Alembic migrations
      ↓
Fresh PostgreSQL database
      ↓
Application starts successfully
```

Test migrations on a clean database.

Do not depend on a manually modified development database.

## 6.2 Required indexes

Inspect real queries before adding indexes.

At minimum evaluate:

```text
messages.conversation_id
messages.created_at
messages.client_message_id
messages.sender_user_id

conversation_participants.conversation_id
conversation_participants.user_id

connection_requests.sender_user_id
connection_requests.receiver_user_id
connection_requests.status
```

For message retrieval, evaluate a composite index appropriate to the actual query/order pattern, for example:

```text
(conversation_id, created_at, id)
```

Do not add indexes blindly.

## 6.3 Constraints and uniqueness

Verify database-level constraints for:

- Unique conversation membership where applicable.
- Unique `client_message_id` / idempotency semantics where applicable.
- Valid connection-request state.
- Foreign keys.
- Required NOT NULL fields.
- Duplicate direct conversation prevention.

Application validation alone is not sufficient for critical uniqueness guarantees.

## 6.4 Backup and restore

Before production:

- Define PostgreSQL backup strategy.
- Verify a backup can actually be restored.
- Document recovery steps.

### Definition of Done

- [ ] Fresh DB can be created from migrations.
- [ ] All production migrations run successfully.
- [ ] Critical indexes exist.
- [ ] Critical uniqueness constraints exist.
- [ ] Backup procedure exists.
- [ ] Restore procedure has been tested.

---

# 7. Phase 3 — Message System Reliability

## Priority: P0

Chat is the core product. Message delivery must be reliable.

## 7.1 Cursor-based pagination

Replace offset pagination for messages where appropriate.

Avoid:

```text
?page=10&limit=50
```

Prefer a stable cursor based on:

```text
created_at + id
```

Example:

```http
GET /messages?before_created_at=...&before_id=...&limit=50
```

The exact API shape must follow existing project conventions.

Use deterministic ordering:

```text
created_at DESC, id DESC
```

or the equivalent established ordering.

### Requirements

- No duplicate messages between pages.
- No skipped messages when new messages arrive.
- Stable behavior when messages have identical timestamps.
- Works with infinite scroll / load older messages.
- Works for both Web and future Mobile clients.

---

# 8. Phase 4 — Message Idempotency

## Priority: P0

Prepare the message API for unreliable networks and future mobile clients.

Every client-generated message should have a stable:

```text
client_message_id
```

Flow:

```text
Client
  ↓
client_message_id = ABC123
  ↓
Backend
  ↓
Save message
  ↓
Return message
```

If the client retries:

```text
client_message_id = ABC123
```

the backend must not create a duplicate message.

Expected behavior:

```text
First request  → create message
Retry request  → return existing message
```

This is essential for:

- Web retry
- Mobile unstable networks
- Offline queue
- WebSocket reconnect
- Request timeout recovery

### Definition of Done

- [ ] Duplicate client message IDs cannot create duplicate messages.
- [ ] Retry behavior is deterministic.
- [ ] Tests cover duplicate requests.
- [ ] API contract documents idempotency behavior.

---

# 9. Phase 5 — WebSocket Reliability

## Priority: P0

The current WebSocket manager can remain in-memory for a single-instance deployment.

Do not implement Redis Pub/Sub yet unless the deployment uses multiple FastAPI instances.

## 9.1 Authentication

Verify WebSocket authentication is secure and follows the existing architecture.

The server must verify:

- User identity.
- Token/ticket validity.
- Expiration.
- Connection authorization.

Never trust user IDs supplied by the client.

## 9.2 Heartbeat

Implement or verify:

```text
Server → Ping
Client → Pong
```

at a reasonable interval, approximately 30 seconds.

Dead connections must be removed.

## 9.3 Reconnect

Frontend should automatically reconnect after an unexpected disconnect.

Requirements:

- Exponential/backoff strategy where appropriate.
- Do not create duplicate WebSocket connections.
- Do not duplicate event subscriptions.
- Re-authenticate when required.
- Re-sync state after reconnect.

## 9.4 Event protocol

Document the event format.

At minimum standardize events such as:

```text
NEW_MESSAGE
MESSAGE_RECALLED
MESSAGE_UPDATED
TYPING
READ_RECEIPT
CONNECTION_REQUEST
```

Only include events that already exist or are actually implemented.

Example:

```json
{
  "type": "MESSAGE_RECALLED",
  "conversation_id": "...",
  "message_id": "...",
  "deleted_at": "..."
}
```

Web and Mobile should eventually consume the same protocol.

### Definition of Done

- [ ] Authentication is verified.
- [ ] Heartbeat works.
- [ ] Dead connections are cleaned up.
- [ ] Reconnect works.
- [ ] Duplicate subscriptions are prevented.
- [ ] Event payloads are documented.
- [ ] Message recall is realtime on both clients.

---

# 10. Phase 6 — Authentication and Authorization Audit

## Priority: P0

Audit every core endpoint.

At minimum:

```text
Users
Conversations
Conversation Participants
Messages
Connection Requests
Recommendations
AI endpoints
WebSockets
```

For every endpoint verify:

```text
Authentication
      ↓
Resource ownership
      ↓
Participant membership
      ↓
Action authorization
```

Important rules:

### Messages

Only the sender can recall their message.

### Conversations

Only participants can access the conversation.

### Connection Requests

- Sender can cancel.
- Receiver can accept/reject.
- Unrelated users cannot modify requests.

### WebSocket

User can only subscribe to authorized conversations.

### AI

User A must never retrieve User B's private conversation/memory data through AI search or RAG.

This last point is particularly important for MemoryChat.

---

# 11. Phase 7 — Security Hardening

## Priority: P0

Audit:

- CORS
- CSRF where applicable
- Authentication
- Authorization
- Rate limiting
- Request size limits
- File upload limits if files exist
- Input validation
- SQL injection safety
- XSS-safe rendering
- Secret management
- Production debug settings

Never deploy with:

```text
DEBUG=true
development secrets
hard-coded API keys
hard-coded database passwords
```

Use environment variables / secret management.

Create a production environment checklist.

---

# 12. Phase 8 — API Contract Stabilization

## Priority: P0

Because a mobile application will be built later, the backend API must become the stable contract shared by:

```text
             FastAPI
             /     \
            /       \
         Web       Mobile
```

Standardize:

## Authentication

Document:

- Login
- Logout
- Refresh/session behavior
- Unauthorized response

## Errors

Use a consistent error shape.

Example:

```json
{
  "detail": "...",
  "code": "..."
}
```

Follow the project's actual convention instead of introducing a second format.

## Pagination

Document cursor semantics.

## Message

Document:

```text
id
conversation_id
sender_id
content
created_at
deleted_at
client_message_id
```

as applicable.

## WebSocket

Document:

```text
event type
payload
authentication
reconnect expectations
```

### Definition of Done

A future mobile developer should be able to build the chat client without reading the backend implementation.

---

# 13. Phase 9 — Frontend Performance Baseline

## Priority: P1

Do not optimize blindly.

First measure.

## 13.1 Message pagination

Load only a bounded number of messages.

Target:

```text
50–100 messages per request
```

Use the cursor to load older messages.

## 13.2 React Query

Verify:

- Correct cache keys.
- No unnecessary refetching.
- Correct invalidation.
- No duplicate requests.
- Correct WebSocket cache updates.

For example:

```text
["messages", conversationId]
```

must remain consistent throughout the application.

## 13.3 Prefetching

Where useful, prefetch conversation data when the user is likely to open it.

Do not prefetch every conversation simultaneously.

## 13.4 Virtualization

Do not add virtualization solely because the application might eventually have large chats.

First implement cursor pagination.

Then benchmark.

If large conversations cause measurable rendering problems, introduce a virtualization library such as `react-virtuoso` using the existing UI architecture.

---

# 14. Phase 10 — Offline / Retry Foundation

## Priority: P1

The full offline-first system can come later, but the architecture must not prevent it.

At minimum:

- Preserve `client_message_id`.
- Handle network timeout.
- Avoid duplicate sends.
- Distinguish:
  - sending
  - sent
  - failed
  - retrying

Recommended future model:

```text
User sends
    ↓
Optimistic message
    ↓
Outbox
    ↓
Send
    ├── success → sent
    └── failure → retry
```

Do not build a large IndexedDB/mobile storage layer during this phase unless the current product requirements demand it.

---

# 15. Phase 11 — AI Reliability

## Priority: P0/P1 depending on current production AI usage

The core chat path must not depend on a slow AI request.

Avoid:

```text
User sends message
        ↓
LLM
        ↓
ChromaDB
        ↓
Insight
        ↓
API response
```

Prefer:

```text
User sends message
        ↓
Save message
        ↓
Return immediately
        │
        └──► Background AI job
                 ↓
             LLM / Chroma
                 ↓
             AI result
                 ↓
           WebSocket event
```

AI failures must not prevent normal chat.

## AI tasks to consider for background processing

- Embedding generation
- Memory extraction
- Insight generation
- Recommendations
- Conversation summarization
- Other expensive AI analysis

Use the project's existing queue/worker infrastructure if present.

If no queue exists, evaluate the simplest production-appropriate worker architecture.

Do not introduce Celery + RabbitMQ + Redis simultaneously without a concrete need.

---

# 16. Phase 12 — ChromaDB / RAG Isolation

## Priority: P1

PostgreSQL remains the transactional source of truth.

ChromaDB stores semantic/vector information.

Expected relationship:

```text
PostgreSQL
    │
    │ source data
    ▼
AI Worker
    │
    ├── Embedding
    ▼
ChromaDB
```

If ChromaDB or the LLM is temporarily unavailable:

```text
Chat
  ↓
must continue working
```

AI features may degrade gracefully.

Also verify strict user/conversation isolation in retrieval.

A user's AI search must never retrieve another user's private data.

---

# 17. Phase 13 — Observability

## Priority: P0

Production must provide enough visibility to diagnose failures.

## Logs

Log structured events for:

- API errors
- Authentication failures
- WebSocket connect/disconnect
- Message processing failures
- AI worker failures
- Database failures

Never log:

- Passwords
- Tokens
- Secrets
- Sensitive message content unnecessarily

## Metrics

Track at least:

```text
API latency
API 4xx/5xx rate
Database latency
WebSocket connections
WebSocket disconnects
Message send failures
Message delivery latency
AI job duration
AI job failures
Queue backlog
```

## Health checks

Provide health endpoints suitable for deployment infrastructure.

Separate:

```text
liveness
readiness
```

where appropriate.

---

# 18. Phase 14 — Production Configuration

## Priority: P0

Create a clear production configuration model.

Separate:

```text
development
test
staging
production
```

Verify:

- Database URL
- Authentication secrets
- CORS origins
- Frontend API URL
- WebSocket URL
- AI provider keys
- Chroma configuration
- Redis configuration if used
- Logging level
- Debug flag

No production secrets in Git.

---

# 19. Phase 15 — Build and Deployment Reproducibility

## Priority: P0

The application must be reproducible from a clean environment.

Verify:

```text
Fresh environment
      ↓
Install dependencies
      ↓
Run migrations
      ↓
Build frontend
      ↓
Start backend
      ↓
Start frontend
      ↓
Health checks
      ↓
Application works
```

Document the deployment process.

A new machine/server should not require undocumented manual fixes.

---

# 20. Phase 16 — CI/CD

## Priority: P0

Set up CI before production deployment.

Recommended pipeline:

```text
Push / Pull Request
        │
        ▼
┌───────────────────┐
│ Backend Tests     │
├───────────────────┤
│ Frontend Lint     │
├───────────────────┤
│ Typecheck         │
├───────────────────┤
│ Build             │
├───────────────────┤
│ E2E               │
└─────────┬─────────┘
          │
          ▼
       PASS?
       /    \
     YES     NO
      │       │
      ▼       ▼
   Deploy    Block
```

Production deployment should never happen when required checks fail.

---

# 21. Phase 17 — Staging Environment

## Priority: P0

Before production:

```text
Local
  ↓
CI
  ↓
Staging
  ↓
Smoke test
  ↓
Production
```

Staging should resemble production as closely as practical.

Run:

- Login
- Connection request
- Accept/reject/cancel
- Send message
- Receive message
- Recall message
- WebSocket reconnect
- AI features
- Logout

---

# 22. Phase 18 — Production Smoke Tests

## Priority: P0

After deployment, manually verify:

### Authentication

```text
Register/login/logout
```

### Connection

```text
Send request
Accept
Reject
Cancel
```

### Chat

```text
Send
Receive
Reconnect
Pagination
```

### Recall

```text
Recall own message
Realtime update
Reload persistence
Unauthorized recall
```

### AI

```text
Recommendation
AI Search
Copilot
```

Only test AI features that are actually enabled in the production release.

---

# 23. Phase 19 — Rollback Plan

## Priority: P0

Document:

```text
How to deploy previous frontend version
How to deploy previous backend version
How to rollback database migrations safely
How to restore database backup
How to disable problematic AI features
```

Do not deploy a database migration that cannot be safely handled during rollback.

Prefer backward-compatible migrations:

```text
Add new field
      ↓
Deploy compatible backend
      ↓
Migrate data
      ↓
Start using new field
```

Avoid destructive migrations in the same release unless explicitly planned.

---

# 24. Phase 20 — Mobile Readiness Check

## Priority: P1

Do not build the mobile app yet in this phase.

Instead ensure the backend is mobile-ready.

Verify:

- REST APIs are independent of browser-specific behavior.
- Authentication can be consumed by mobile.
- API response formats are stable.
- Cursor pagination works.
- Message idempotency exists.
- WebSocket protocol is documented.
- Reconnect behavior is documented.
- Conversation permissions are enforced server-side.
- Message state is represented explicitly.
- Push notification architecture can be added later.

Future architecture:

```text
                 FastAPI
                /       \
               /         \
            Next.js      Mobile
               \         /
                \       /
              Shared API
                   │
              Shared WS
                   │
              PostgreSQL
```

---

# 25. Things NOT to Implement Before First Deployment

Unless actual deployment requirements demand them, defer:

## P2 — Scale-only infrastructure

- Kubernetes
- Docker Swarm
- Multiple FastAPI instances
- Redis WebSocket Pub/Sub
- Read replicas
- Database sharding
- Complex distributed locking
- Semantic cache
- Large-scale vector optimization
- Complex event streaming
- Microservice decomposition

The first production release should remain as simple as possible.

---

# 26. Recommended First Production Architecture

For the initial deployment, prefer:

```text
                    Internet
                       │
                       ▼
                Reverse Proxy
                       │
              ┌────────┴────────┐
              ▼                 ▼
         Next.js             FastAPI
                                │
                     ┌──────────┼──────────┐
                     ▼          ▼          ▼
                PostgreSQL    Redis      AI Worker
                                           │
                                      ┌────┴────┐
                                      ▼         ▼
                                   LLM      ChromaDB
```

Redis is optional if the current system does not need it yet.

Keep:

```text
PostgreSQL = source of truth
FastAPI = application/API layer
WebSocket = realtime layer
AI Worker = asynchronous AI processing
ChromaDB = semantic/vector storage
```

---

# 27. Final Pre-Deployment Checklist

## Architecture

- [ ] README is accurate.
- [ ] AGENTS.md reflects current development rules.
- [ ] ARCHITECTURE.md reflects current architecture.
- [ ] Important decisions are documented.
- [ ] No duplicate architectural patterns exist.

## Database

- [ ] PostgreSQL production configuration works.
- [ ] Migrations work from a clean database.
- [ ] Critical indexes exist.
- [ ] Critical uniqueness constraints exist.
- [ ] Backup works.
- [ ] Restore has been tested.

## Backend

- [ ] Authentication is production-ready.
- [ ] Authorization is enforced.
- [ ] Message ownership is enforced.
- [ ] Connection permissions are enforced.
- [ ] Cursor pagination works.
- [ ] Message idempotency works.
- [ ] Error responses are consistent.
- [ ] Health checks work.

## WebSocket

- [ ] Authentication works.
- [ ] Heartbeat works.
- [ ] Dead connections are cleaned up.
- [ ] Reconnect works.
- [ ] Duplicate connections/subscriptions are handled.
- [ ] Event protocol is documented.
- [ ] Recall updates both clients.

## Frontend

- [ ] Production build works.
- [ ] Lint passes.
- [ ] Typecheck passes.
- [ ] React Query cache behavior is correct.
- [ ] Message pagination works.
- [ ] Critical UI flows work.

## AI

- [ ] AI does not block normal message delivery.
- [ ] AI failures degrade gracefully.
- [ ] RAG access respects user/conversation permissions.
- [ ] Expensive AI work can run asynchronously where necessary.

## Security

- [ ] No secrets committed.
- [ ] Production debug mode disabled.
- [ ] CORS restricted.
- [ ] Rate limiting considered for public endpoints.
- [ ] Upload limits enforced if applicable.
- [ ] WebSocket authorization enforced.
- [ ] AI retrieval isolation verified.

## Testing

- [ ] `pytest` passes.
- [ ] `npm run lint` passes.
- [ ] `npm run typecheck` passes.
- [ ] Playwright E2E passes.
- [ ] Critical manual smoke tests pass.

## CI/CD

- [ ] CI runs automatically.
- [ ] Failed tests block deployment.
- [ ] Production build is reproducible.
- [ ] Staging deployment works.
- [ ] Production deployment is documented.
- [ ] Rollback procedure exists.

## Observability

- [ ] Structured logs exist.
- [ ] API errors are visible.
- [ ] WebSocket failures are visible.
- [ ] AI worker failures are visible.
- [ ] Health checks exist.
- [ ] Basic latency/error metrics exist.

## Mobile readiness

- [ ] API contract is documented.
- [ ] Cursor pagination is stable.
- [ ] Message idempotency exists.
- [ ] WebSocket protocol is documented.
- [ ] Reconnect behavior is documented.
- [ ] Server-side authorization is complete.
- [ ] Push notification can be added later without redesigning chat.

---

# 28. Execution Order

The AI agent should implement this plan in the following order:

```text
Phase 0  → Repository / Architecture Baseline
Phase 1  → Test Suite Stabilization
Phase 2  → Database Production Readiness
Phase 3  → Message Cursor Pagination
Phase 4  → Message Idempotency
Phase 5  → WebSocket Reliability
Phase 6  → Auth / Authorization Audit
Phase 7  → Security Hardening
Phase 8  → API Contract Stabilization
Phase 9  → Frontend Performance Baseline
Phase 10 → Offline / Retry Foundation
Phase 11 → AI Reliability / Background Jobs
Phase 12 → ChromaDB / RAG Isolation
Phase 13 → Observability
Phase 14 → Production Configuration
Phase 15 → Reproducible Build / Deployment
Phase 16 → CI/CD
Phase 17 → Staging
Phase 18 → Production Smoke Test
Phase 19 → Rollback Plan
Phase 20 → Mobile Readiness Check
```

Do not execute all phases blindly.

For each phase:

```text
Inspect
  ↓
Plan
  ↓
Implement
  ↓
Test
  ↓
Verify
  ↓
Update documentation
  ↓
Proceed to next phase
```

If an existing architecture conflicts with a proposed change, stop and report the conflict before performing a large refactor.

---

# 29. Definition of Pre-Deployment Complete

The project is ready for the first production deployment when:

1. Core chat functionality is reliable.
2. Authentication and authorization are verified.
3. Message pagination is stable.
4. Message sending is idempotent.
5. WebSocket reconnect/heartbeat works.
6. Critical tests pass.
7. CI blocks broken builds.
8. Production configuration is reproducible.
9. Staging smoke tests pass.
10. Backups and rollback are documented.
11. Logs and health checks are available.
12. AI failures cannot take down core chat.
13. API/WebSocket contracts are stable enough for future Mobile.
14. No critical security issue remains unresolved.

**Do not consider the project production-ready merely because `npm run dev` and `make run` work locally.**
