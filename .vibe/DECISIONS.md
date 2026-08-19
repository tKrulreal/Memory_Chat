# Architecture & Product Decisions

## DEC-001 — Unidirectional WebSocket Communication

**Status:** Accepted

**Date:** 2026-08-19

### Decision
WebSockets are used strictly for **server-to-client** push events. Clients must use standard REST API requests (e.g., `POST /messages`) to send data to the server.

### Context
Real-time chat applications require instantaneous updates across clients. Fully bi-directional WebSockets add complexity in handling authentication, payload validation, and error responses compared to standard REST endpoints.

### Reasoning
By limiting WebSockets to server-to-client broadcasts, the system leverages FastAPI's robust REST request validation (Pydantic), standard HTTP error codes, and existing JWT authentication middlewares for all inbound actions. The WebSocket connection merely serves as an event stream to trigger UI updates.

### Consequences
#### Benefits
- Simplifies input validation by reusing REST endpoints.
- Standard HTTP status codes (e.g., 403 Forbidden for recall authorization) work seamlessly.
#### Trade-offs
- Slight overhead for clients sending messages (HTTP handshake vs raw WS frame).

### Current Implementation
- `src/api/ws.py` explicitly ignores incoming payload data (except ping/pong).
- `frontend/components/ws/ws-bootstrap.tsx` only listens for events and updates the React Query cache.


## DEC-002 — Transactional Outbox Pattern for Background Tasks

**Status:** Accepted

**Date:** 2026-08-19

### Decision
Side-effects (like triggering AI memory extraction) are not executed synchronously or pushed directly to an external queue. Instead, an event is written to the `outbox_events` table within the same PostgreSQL/SQLite transaction as the core entity changes. An `OutboxWorker` then publishes these to an In-Memory `EventBus`.

### Context
When a user sends a message, the system must eventually run an AI summarization task. If the API publishes to a queue directly and the database transaction fails, the AI processes phantom data. If the DB commits but the queue fails, the AI task is lost.

### Reasoning
The Transactional Outbox pattern guarantees *at-least-once* delivery. If the server crashes immediately after a message is sent, the outbox record remains in the database and will be processed when the server restarts.

### Consequences
#### Benefits
- Strong data consistency between core chat logic and AI processing.
- AI operations (which are slow) do not block the REST API response.
#### Trade-offs
- Adds database write overhead for every significant action.

### Current Implementation
- `src/models/ai.py` contains `OutboxEvent`.
- `src/workers/outbox_worker.py` polling logic and `src/events/bus.py`.
- `src/workers/memory_worker.py` acts upon these events.


## DEC-003 — Message Recall via Soft Deletion

**Status:** Accepted

**Date:** 2026-08-19

### Decision
Recalling a message does not delete the record from the database. Instead, it sets a `deleted_at` timestamp. The frontend obscures the content dynamically based on this timestamp.

### Context
Users need the ability to "undo" or recall a sent message. However, hard-deleting records complicates database integrity, auditing, and vector database syncing (since the AI might have already ingested the message).

### Reasoning
Soft deletion maintains the chronological integrity of the conversation. The AI and system admins maintain a permanent record, while the UI respects the user's intent to hide the message from the active conversation view. Furthermore, strict backend authorization ensures only the original sender can trigger this soft deletion.

### Consequences
#### Benefits
- Audit trails are preserved.
- Database foreign key constraints remain intact.
- Prevents cross-user data manipulation.
#### Trade-offs
- Frontend logic must remember to check `deleted_at` before rendering content.

### Current Implementation
- `src/models/chat.py` defines `deleted_at` on `Message`.
- `MessageService.delete_message` validates ownership and sets the timestamp.
- `MessageBubble.tsx` overrides the text with *"Tin nhắn đã được thu hồi"* if `deleted_at` is not null.


## DEC-004 — LangChain `bind_tools` over LangGraph for Copilot

**Status:** Accepted

**Date:** 2026-08-19

### Decision
The AI Copilot orchestrator relies on LangChain's native `bind_tools` functionality to dynamically invoke tools in a single-turn loop, rather than using a complex LangGraph state machine.

### Context
The original documentation and architecture plans specified LangGraph. However, building and maintaining a full LangGraph state machine for simple tool retrieval (search, get info, suggest reply) introduced unnecessary complexity for the MVP.

### Reasoning
LangChain's native tool calling provides sufficient reasoning capabilities for the current feature set. A `DummyGraph` was implemented to satisfy the existing interface while utilizing a simpler execution path.

### Consequences
#### Benefits
- Easier to debug and trace tool calls.
- Lower latency for synchronous Copilot requests.
#### Trade-offs
- Limits the ability to handle complex, multi-step, cyclical agent workflows in the future.

### Current Implementation
- `src/agents/orchestrator.py` defines `DummyGraph` and uses `chat_model.bind_tools(tools)` in `run_copilot`.


## DEC-005 — Strict P2P Conversation Model

**Status:** Accepted

**Date:** 2026-08-19

### Decision
Conversations are modeled strictly as Peer-to-Peer (Direct) with explicit `user_a_id` and `user_b_id` columns, rather than using an abstract `ConversationParticipant` pivot table.

### Context
The MVP requires direct messaging between users who have established a connection.

### Reasoning
Hardcoding two user IDs directly on the `Conversation` table drastically simplifies database queries, indexing, and authorization checks. It avoids complex joins required by a many-to-many participant architecture.

### Consequences
#### Benefits
- Highly performant queries for listing and securing conversations.
- Simplified backend logic.
#### Trade-offs
- Group chats cannot be implemented without a significant database schema migration in the future.

### Current Implementation
- `src/models/chat.py` -> `Conversation` table.


---

# Decision Conflicts Requiring Human Review

## CONFLICT-001 — Horizontal Scaling vs. In-Memory Components

**What the code does:**
The system uses an `In-Memory` `ConnectionManager` for WebSockets and an `In-Memory` `EventBus` for background workers.

**What the documentation says / Configuration implies:**
The project includes a `docker-compose.yml` and is structured to scale out as a containerized microservice backend.

**Why the difference matters:**
If multiple FastAPI instances are deployed behind a load balancer, User A (connected to Instance 1) cannot send real-time WebSocket events to User B (connected to Instance 2). Similarly, in-memory event buses will fragment across instances.

**Decision needed:**
Should the project officially adopt **Redis** for WebSocket Pub/Sub and Celery/RabbitMQ for background tasks, or should we document that the architecture is strictly limited to a single monolithic backend instance?
