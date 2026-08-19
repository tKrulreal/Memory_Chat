# MemoryChat: Long-Term Product & Engineering Memory

This document preserves the long-term vision and core principles of the MemoryChat project. It serves as a stable anchor for future development and a guide for AI agents to understand the project's foundational identity.

## 1. Product Vision

**MemoryChat is an "Intelligent Inbox" that turns conversations into actionable, long-term memory.**

Unlike standard chat applications where messages disappear into a difficult-to-search history, MemoryChat uses background AI to continuously extract facts, summarize context, and build relationship profiles. It allows users to query their past conversations naturally, understand their connections deeply, and receive proactive, context-aware suggestions—without sacrificing real-time communication speed.

## 2. Product Identity: What Makes MemoryChat Different?

In a standard chat app:
`Conversation → Stored History → Manual Keyword Search`

In MemoryChat:
`Conversation → Background Extraction → Contextual Memory → Copilot Understanding → Proactive Recommendations`

## 3. Core Product Principles

### Privacy & Isolation
Private conversations and memories must remain strictly isolated. The AI must never retrieve or leak context from one user's private conversations into another user's session.

### Core Independence
Core P2P communication (sending, receiving, and recalling messages) is the primary utility. It must remain fully functional and blazing fast even if the AI providers, ChromaDB, or background workers fail.

### Human-in-the-Loop
AI exists to assist, suggest, and summarize. It must never take irreversible social actions—such as sending a message or accepting a connection request—without explicit user confirmation.

### Consistent State
Data integrity is paramount. If a user deletes or recalls a message, the system must respect that intent consistently across both the traditional database and the AI vector store.

## 4. The Role of AI

**AI Should:**
- Summarize long, idle conversations in the background.
- Extract factual data (skills, interests) to build robust contact profiles.
- Answer natural language queries about past conversations (Semantic Search).
- Suggest follow-up actions, replies, or new connections.

**AI Should NOT:**
- Automatically send messages to other users.
- Become the source of truth for transactional data (e.g., who is connected to whom).
- Override explicit user settings or decisions.
- Block the real-time REST/WebSocket event loops while processing.

## 5. Long-Term Architecture Principles

- **PostgreSQL is Authoritative:** Transactional data (users, messages, connections) lives in Postgres/SQLite. Vector databases (ChromaDB) are strictly for caching derived AI context.
- **Event-Driven AI:** All heavy AI operations must be decoupled from the synchronous HTTP request-response cycle via the Transactional Outbox pattern and EventBus.
- **Incremental Scaling:** The system relies on monolithic, in-memory components (WebSocket Manager, EventBus) for speed and simplicity. Distributed infrastructure (Redis, Celery, Kubernetes) should only be introduced when vertical scaling limits are actually hit, not prematurely.
- **Shared API Contracts:** The backend APIs should be agnostic enough to support potential future mobile clients without requiring web-specific hacks.

## 6. Development Horizons

### Now (Current Focus)
- Stable, real-time P2P messaging using unidirectional WebSockets.
- Reliable connection request workflows.
- Accurate background AI extraction via `MemoryWorker`.
- Functional LangChain Copilot for searching past context.

### Next (Near Future)
- Fixing unstable legacy backend tests.
- Transitioning from offset-based pagination to cursor-based pagination for messages.
- Migrating long-running Outbox events to a proper task queue to prepare for scaling.

### Later (Long-Term Possibilities)
- Horizontal scaling with a Redis Pub/Sub backplane for WebSockets.
- Mobile application clients.
- Push notifications for offline users.
- Group conversations (requires significant schema migration).

## 7. Explicit Non-Goals

MemoryChat should **NOT** become:
- A traditional enterprise CRM.
- An autonomous agent platform where AI talks to AI on behalf of users.
- A fully decentralized/blockchain messaging protocol.
- Dependent on distributed microservices before the user base demands it.

## 8. Open Product Questions
*These questions require human product decisions and are not yet settled.*
- **Data Retention:** How much historical conversational memory should users control, and should they be able to explicitly wipe the AI's memory of a specific person?
- **AI Hub Prominence:** Should the AI Copilot remain a slide-out assistant, or should it eventually become the primary interface (e.g., an AI that you text directly to interact with the app)?
- **Mobile Strategy:** When mobile clients are built, will they be React Native (sharing Next.js logic) or fully native?

---

## 9. Relationship With Other Documentation

- **`README.md`** → What the project is and how to run it.
- **`AGENTS.md`** → How AI/developers must work on the current repository.
- **`ARCHITECTURE.md`** → How the system technically works today.
- **`DECISIONS.md`** → Why important architectural decisions were made.
- **`WORKLOG.md`** → Implementation progress (What has been done, what remains).
- **`LONG-TERM.md`** (This file) → Where MemoryChat is going and what principles must survive future changes.
