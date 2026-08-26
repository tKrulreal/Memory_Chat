# MEMORYCHAT_RAILWAY_DEPLOYMENT_PLAN.md

# MemoryChat — Railway Production Deployment

## Context

The entire `MEMORYCHAT_PRE_DEPLOYMENT_PLAN.md` has already been completed.

All 20 pre-deployment phases have been implemented and verified.

**Do NOT repeat the pre-deployment phases.**

The project is now moving from:

```text
Development / Pre-Deployment
            ↓
       Railway Staging
            ↓
      Production
```

The goal is to deploy the **current MemoryChat application** to Railway safely and reproducibly.

---

# 1. Deployment Principles

1. The 20 pre-deployment phases are considered complete.
2. Do not reopen completed pre-deployment work unless an actual deployment blocker is discovered.
3. Do not redesign the application architecture unnecessarily.
4. Prefer the simplest reliable Railway architecture.
5. Keep PostgreSQL as a separate persistent database service.
6. Never commit production secrets.
7. Never expose backend secrets to the frontend.
8. Do not deploy directly to production before staging/smoke verification.
9. Every deployment step must be verifiable.
10. Do not modify unrelated application code.

---

# Phase 1 — Deployment Reconnaissance

## Goal

Inspect the current repository and determine exactly how MemoryChat should be deployed on Railway.

Read:

- `README.md`
- `AGENTS.md`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- `long-term.md`
- `WORKLOG.md`
- `JOURNAL.md`
- `MEMORYCHAT_PRE_DEPLOYMENT_PLAN.md`

Inspect:

### Backend

- FastAPI entry point
- `requirements.txt` / `pyproject.toml`
- ASGI startup command
- environment configuration
- database configuration
- Alembic
- WebSocket implementation
- background workers
- AI services
- ChromaDB
- filesystem dependencies
- health endpoints

### Frontend

- Next.js configuration
- `package.json`
- Dockerfiles
- API configuration
- WebSocket configuration
- environment variables
- production build/start commands

### Infrastructure

Inspect:

- Dockerfiles
- Docker Compose
- Makefile
- CI/CD
- `.env.example`
- `.gitignore`

Determine:

- Required Railway services
- Services that can share a container
- Services that require persistent storage
- Required volumes
- Required environment variables
- Build commands
- Start commands
- Health checks
- Deployment blockers

### Output

Do not deploy yet.

Report:

```text
Current Deployment Architecture
Required Railway Services
Required Persistent Volumes
Required Environment Variables
Build Commands
Start Commands
Potential Blockers
Recommended Railway Architecture
```

---

# Phase 2 — Docker Production Readiness

## Goal

Ensure the current application can be built and run as production Docker containers.

Inspect existing Dockerfiles first.

Do not create new Dockerfiles if the current ones are already suitable.

## Backend

Verify:

```bash
docker build
docker run
```

The backend container must:

- start successfully
- expose the correct port
- connect to PostgreSQL
- run FastAPI correctly
- support WebSocket connections
- use production configuration
- not depend on localhost services

## Frontend

Verify:

```bash
docker build
docker run
```

The frontend container must:

- build successfully
- start successfully
- connect to the configured production API
- use the correct WebSocket URL
- not contain hardcoded localhost URLs

## Railway Port

Railway provides a dynamic `$PORT`.

Do not hardcode a production port when the Railway runtime requires `$PORT`.

---

# Phase 3 — Railway Project Architecture

Create the simplest architecture required by the current application.

Expected initial architecture:

```text
Railway Project
│
├── frontend
│   └── Next.js
│
├── backend
│   └── FastAPI
│
├── PostgreSQL
│   └── Railway PostgreSQL
│
└── ChromaDB / persistent AI storage
    └── only if required
```

Do not automatically create a separate ChromaDB service.

First inspect how ChromaDB is currently used.

If ChromaDB requires persistent local storage, evaluate:

- Railway Volume
- Separate ChromaDB service + volume
- Backend + ChromaDB in the same service with a mounted volume

Choose the simplest reliable option based on the current implementation.

Do not introduce infrastructure that is not required.

---

# Phase 4 — Environment Variables and Secrets

Create a production environment-variable checklist.

## Backend

Identify only variables actually used by the repository, such as:

```text
DATABASE_URL
JWT_SECRET
LLM_API_KEY
AI_PROVIDER_KEY
CHROMA_CONFIGURATION
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
```

## Frontend

Identify only variables actually required, such as:

```text
NEXT_PUBLIC_API_URL
NEXT_PUBLIC_WS_URL
```

## Rules

- Never commit production `.env` files.
- Never expose backend secrets through `NEXT_PUBLIC_*`.
- Never expose LLM, database, JWT, Twilio, or other private credentials in browser code.
- Use Railway Variables for production secrets.
- Keep `.env.example` updated with variable names only.
- Never put real secret values in documentation.

Produce a table:

| Variable | Service | Required | Secret | Purpose |
|---|---|---|---|---|

---

# Phase 5 — PostgreSQL and Database Migration

Use Railway PostgreSQL for the production transactional database.

Do not run production PostgreSQL inside the frontend/backend container.

Deployment flow:

```text
Railway PostgreSQL
        ↓
DATABASE_URL
        ↓
Backend
        ↓
Alembic
        ↓
alembic upgrade head
        ↓
Verify schema
        ↓
Verify indexes
```

Rules:

- Use Alembic migrations.
- Do not replace migrations with `create_all()`.
- Do not delete/recreate production data.
- Do not modify migration history without a verified reason.
- Verify the final schema.
- Verify important indexes.
- Establish backups and a restore strategy.

---

# Phase 6 — Backend Deployment

Deploy FastAPI as a Railway service.

Verify:

- production startup command
- dynamic Railway `$PORT`
- health endpoint
- database connectivity
- authentication
- authorization
- CORS
- production logging
- error handling
- WebSocket connectivity
- graceful shutdown where applicable

Do not claim the backend is healthy merely because the container starts.

Verify an actual HTTP health request.

---

# Phase 7 — WebSocket / Realtime Deployment

This is a critical part of MemoryChat.

Verify:

```text
Browser
   ↓
WSS
   ↓
Railway
   ↓
FastAPI WebSocket
```

Test:

- WebSocket connection
- authentication
- reconnect
- connection cleanup
- `NEW_MESSAGE`
- `MESSAGE_RECALLED`
- connection request events
- multiple browser sessions

Verify that:

- HTTP works
- WebSocket works
- WebSocket events reach the correct users
- reconnect does not create duplicate connections
- realtime state remains consistent with persisted database state

Do not assume WebSocket support merely because HTTP works.

---

# Phase 8 — Frontend Deployment

Deploy Next.js as a Railway service.

Verify:

- production build
- production start command
- API URL
- WebSocket URL
- authentication
- cookies/session/JWT behavior
- CORS
- routing
- static assets

Search the production configuration for:

```text
localhost
127.0.0.1
0.0.0.0
```

No browser-facing production configuration should accidentally point to local development services.

---

# Phase 9 — ChromaDB / AI Persistence

Inspect the current ChromaDB implementation before deciding the deployment model.

Determine:

- Where ChromaDB data is stored.
- Whether it requires persistent filesystem storage.
- Whether it is embedded or a separate service.
- Whether the current AI workers depend on local files.
- Whether the data can be rebuilt from PostgreSQL/source data.
- Whether a Railway Volume is required.

If a Railway Volume is required:

```text
ChromaDB
   ↓
Persistent Volume
   ↓
Survives container restart/redeploy
```

Do not deploy ChromaDB using ephemeral container storage if its data must persist.

Verify AI/RAG functionality after deployment.

---

# Phase 10 — Domain and HTTPS

Configure the production domain through Railway.

Verify:

```text
https://your-domain.com
```

and WebSocket:

```text
wss://your-domain.com
```

or the appropriate Railway backend hostname.

Verify:

- DNS
- TLS
- HTTPS
- WSS
- CORS
- secure cookies if applicable
- authentication redirects

Do not expose PostgreSQL publicly unless absolutely required.

---

# Phase 11 — Staging Deployment

Before production, deploy to a staging environment.

Staging should use production-like:

- Docker images
- environment variables
- PostgreSQL
- WebSocket
- HTTPS
- AI configuration
- persistent storage

Run smoke/E2E tests.

## Authentication

- Register
- Login
- Logout
- Invalid credentials
- Expired authentication

## Connection Requests

- Send request
- Receive request
- Accept
- Reject
- Cancel

## Chat

- Open conversation
- Send message
- Receive realtime message
- Refresh
- Load older messages
- Verify cursor pagination
- Recall message
- Verify receiver sees recall in realtime

## AI

Test currently implemented AI features:

- AI Hub
- Copilot
- Recommendations
- Search
- RAG/memory

Verify AI cannot access unauthorized user/conversation data.

## Reliability

Test:

- browser refresh
- WebSocket reconnect
- backend restart
- frontend restart
- database connectivity

---

# Phase 12 — Production Deployment

Only proceed after staging passes.

Recommended release order:

```text
1. Verify Git commit/version
2. Verify Railway environment variables
3. Verify database backup/safety
4. Deploy database migrations
5. Deploy backend
6. Verify backend health
7. Verify WebSocket
8. Deploy frontend
9. Verify frontend
10. Run production smoke tests
11. Monitor logs and metrics
12. Declare deployment successful
```

Do not deploy unrelated code during the production release.

---

# Phase 13 — Rollback

Document rollback procedures.

## Backend

Rollback to the previous known-good Railway deployment.

## Frontend

Rollback to the previous known-good Railway deployment.

## Database

Do not automatically rollback database migrations.

For each production migration determine whether it is:

- backward compatible
- reversible
- forward-fix only

Prefer forward-compatible database migrations.

## Configuration

Restore the previous Railway variables/configuration when necessary.

---

# Phase 14 — Monitoring and Operations

After deployment verify monitoring for:

- HTTP 4xx/5xx
- API latency
- backend errors
- database errors
- database connections
- WebSocket disconnects
- WebSocket connection count
- AI failures
- AI latency
- CPU
- memory
- storage
- deployment failures
- database backup status

Create practical alerts where supported.

Document how to inspect logs and diagnose common failures.

---

# Phase 15 — Cost Control

Document expected monthly cost for:

- Frontend service
- Backend service
- PostgreSQL
- Persistent volumes
- AI API usage
- SMS/OTP if implemented
- Other external services

Prefer the smallest reliable configuration for the initial production release.

Do not add infrastructure merely for hypothetical future scale.

Scale only when actual usage requires it.

---

# Deployment Documentation

Create:

`MEMORYCHAT_RAILWAY_DEPLOYMENT.md`

This document becomes the operational deployment/runbook.

It must contain:

1. Railway architecture
2. Railway services
3. Docker configuration
4. Environment variables
5. Secrets
6. PostgreSQL setup
7. ChromaDB/storage setup
8. Backend deployment
9. Frontend deployment
10. WebSocket configuration
11. Domain configuration
12. Staging deployment
13. Production deployment
14. Smoke tests
15. Monitoring
16. Rollback
17. Troubleshooting
18. Cost considerations

Do not duplicate the completed 20 pre-deployment phases.

Reference `MEMORYCHAT_PRE_DEPLOYMENT_PLAN.md` when historical context is needed.

---

# Execution Rules

## Before provisioning

The agent MUST first:

1. Inspect the repository.
2. Inspect existing Docker setup.
3. Determine required Railway services.
4. Determine ChromaDB persistence requirements.
5. Determine required environment variables.
6. Determine build/start commands.
7. Identify deployment blockers.
8. Produce the proposed Railway architecture.
9. Produce the deployment checklist.

Then STOP and request approval before creating production resources.

## During deployment

- Make small changes.
- Verify each step.
- Do not modify unrelated application code.
- Do not commit secrets.
- Do not delete production data.
- Do not bypass security checks.
- Do not claim success without real verification.
- Stop if a production safety issue is discovered.

Use appropriate ECC agents when useful:

- `architect`
- `security-reviewer`
- `database-reviewer`
- `e2e-runner`
- `code-reviewer`

---

# Final Success Criteria

The deployment is considered successful only when:

```text
Private GitHub
      ↓
Railway Build
      ↓
Frontend deployed       ✅
Backend deployed        ✅
PostgreSQL connected    ✅
Alembic migrations      ✅
HTTPS                   ✅
WSS                     ✅
Authentication          ✅
Connection Requests     ✅
Realtime Chat           ✅
Message Recall          ✅
Cursor Pagination       ✅
AI/RAG                  ✅
Persistence             ✅
E2E/Smoke Tests         ✅
Monitoring              ✅
Rollback documented     ✅
```

The final state should be:

```text
                    🌐 Internet
                         │
                    HTTPS / WSS
                         │
                         ▼
                  ┌──────────────┐
                  │   Railway    │
                  │              │
                  │  Next.js     │
                  │  FastAPI     │
                  │  PostgreSQL  │
                  │  ChromaDB*   │
                  └──────────────┘

* Only if required by the current architecture,
  with persistent storage configured correctly.
```

**Objective: deploy the existing, already-stabilized MemoryChat system to Railway — not redesign the application.**
