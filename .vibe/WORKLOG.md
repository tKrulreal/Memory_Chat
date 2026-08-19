# MemoryChat — Implementation Worklog

This document tracks the implementation progress, features, and fixes for the MemoryChat platform.

## What has been completed?

### Phase 1: MVP Setup & Documentation
- `[x]` Initialize project (FastAPI, React, Vite)
- `[x]` Database schema (Alembic migrations up to `00b16a0c0c78`)
- `[x]` Basic WebSocket Manager and EventBus framework
- `[x]` LangChain Copilot implementation (`bind_tools`)
- `[x]` Document `ARCHITECTURE.md` reflecting actual codebase stateoke
- `[x]` Document `README.md` for developer onboarding

### Phase 2: Core Messaging Enhancements
- `[x]` **Feature:** Message Recall (Thu hồi tin nhắn)
  - `[x]` Add strict ownership validation to `delete_message` service (403 Forbidden).
  - `[x]` Broadcast `MESSAGE_RECALLED` event to both sender and receiver.
  - `[x]` Process WebSocket event in frontend (`ws-bootstrap.tsx`) and update React Query cache dynamically.
  - `[x]` Add UI `window.confirm` native dialog for recall action.
  - `[x]` Update `MessageBubble` to obscure original content and display *"Tin nhắn đã được thu hồi"* if `deleted_at` exists.
- `[x]` **Feature:** Chat Sidebar Refactor
  - `[x]` Remove heavy AI Semantic Search dropdown from sidebar search.
  - `[x]` Simplify search input to perform instant local filtering by peer name.

### Phase 3: AI Memory & Analysis
- `[x]` `MemoryWorker` background extraction via ChromaDB.

## What is currently being worked on?
- None (Waiting for next phase).

## What remains?

### Architectural Optimizations
- `[x]` **Optimization:** Migrate from Offset-based pagination to Cursor-based pagination for messages (Completed in Phase 3).
- `[ ]` **Optimization:** Replace `Array.map` with Virtualization (`react-virtuoso`) for chat message lists.
- `[ ]` **Optimization:** Move AI long-running tasks out of the EventBus/FastAPI process into a proper task queue (e.g., Celery) to prevent blocking.
- `[x]` **Phase 4 - Message Idempotency**: Returned 200 OK with existing message on duplicate `client_message_id` instead of 409 Conflict.
- `[x]` **Phase 5 - WebSocket Reliability**: Implemented robust server-side ping/pong heartbeat using background tasks to eagerly drop dead connections, and standardized WS event types (e.g., `SEND_MESSAGE` -> `NEW_MESSAGE`).
- `[x]` **Phase 6 - Auth & Authorization Audit**: Verified zero-trust architecture across all endpoints. Users cannot access others' messages, conversations, connection requests, or AI data. All API endpoints properly enforce `current_user.id` boundaries.
- `[x]` **Phase 7 - Security Hardening**: Added robust `slowapi` rate limiting (100 req/min), injected `RequestSizeLimitMiddleware` (max 10MB default) to prevent DoS, and added strict configuration checks in `get_settings()` to fail fast if default DEV secrets or DEBUG logging are detected in `production`.
- `[x]` **Phase 8 - API Contract Stabilization**: Standardized the global error shape across the FastAPI application (HTTP, Validation, and Rate Limit errors now share `{"error": "...", "message": "..."}`). Documented endpoints, cursor pagination semantics, and WebSocket protocols into `.vibe/API_CONTRACT.md` as the unified source of truth.
- `[x]` **Phase 9 - Frontend Performance Baseline**: Fixed critical `useInfiniteQuery` cache update bug in WebSocket handler. Integrated `react-intersection-observer` for seamless auto-scrolling cursor pagination. Added intelligent `onMouseEnter` prefetching to the conversation list to ensure zero-latency chat loading.
- `[x]` **Phase 10 - Offline / Retry Foundation**: Centralized sending logic to `useSendMessage` hook. Added support for optimistic updates with tracking for "sending", "sent", and "failed" states. Unsuccessful messages are visually marked with a retry option without blocking the user, establishing robust offline-resilient architecture.
- `[x]` **Phase 11 - AI Reliability**: Assessed and refactored the Transactional Outbox worker architecture. Discovered and fixed a critical flaw where `InsightWorker` and `ConnectionRecommendationWorker` were `await`ing slow LLM calls directly in the Outbox processor, blocking the entire queue. Both workers now immediately offload their jobs to `asyncio.create_task` with proper lock deduplication, ensuring AI processing never blocks core chat workflows.
- `[x]` **Phase 12 - ChromaDB / RAG Isolation**: Audited VectorStore integration. Confirmed strict data isolation by verifying `owner_user_id` is natively enforced in ChromaDB `where` clauses. Implemented graceful degradation in `/api/v1/search/conversations` to fall back to a PostgreSQL ILIKE search (by user name/email) if the LLM provider or ChromaDB is temporarily unavailable.
- `[x]` **Phase 13 - Observability**: Separated `/health` into `/health/liveness` and `/health/readiness` probes for deployment readiness. Integrated `prometheus_client` and `prometheus-fastapi-instrumentator` to automatically track API metrics, and instrumented custom metrics for WebSocket active connections, message latency/failures, AI worker durations/failures, and outbox queue backlog.
- `[x]` **Phase 14 - Production Configuration**: Audited configuration files to ensure no production secrets exist in Git. Removed leaked OpenAI key from `.env.example`. Enforced strict security assertions in `src/config.py` for `production` and `staging` environments (JWT secret, debug mode, logging level, CORS wildcards).
- `[x]` **Phase 15 - Build and Deployment Reproducibility**: Created a robust, zero-downtime deployment architecture. Dockerized the Next.js frontend using an ultra-lightweight Multi-stage standalone build. Orchestrated both frontend and backend through `docker-compose.yml` with strict health check dependencies. Authored a `deploy.sh` script and a comprehensive `DEPLOYMENT.md` guide to guarantee 100% reproducibility on any fresh Ubuntu/Linux server.
- `[x]` **Phase 16 - CI/CD**: Established a robust GitHub Actions CI pipeline (`.github/workflows/ci.yml`). Configured three parallel/sequential jobs: Backend tests (`pytest`), Frontend checks (`eslint`, `tsc`, `next build`), and E2E testing (Playwright against a localized `docker-compose` backend).
- `[x]` **Phase 17, 18, 19 - Operations Manuals**: Authored comprehensive runbooks for production operations. Created `docs/SMOKE_TESTING.md` detailing mandatory manual test cases for Staging and Production (Auth, P2P, Chat, Recall, AI). Created `docs/ROLLBACK_PLAN.md` covering Docker revert strategies, Alembic database downgrades, SQLite backup/restore procedures, and AI feature fail-safes.
- `[x]` **Phase 20 - Mobile Readiness Check**: Audited the backend architecture and confirmed it is fully mobile-ready (supports Bearer tokens, URL query ticket auth for WebSockets, Idempotency-Key headers, and Cursor Pagination). Authored `docs/WEBSOCKET_PROTOCOL.md` specifying exact JSON payloads and retry strategies to allow iOS/Android teams to integrate flawlessly.
- `[ ]` **Optimization:** Add Redis Pub/Sub backplane to scale WebSocket `ConnectionManager` horizontally.

## What is blocked?
- None.
