# MemoryChat — SQLite → PostgreSQL Migration & Production Readiness Plan

> **Status:** Ready for agent execution after approval  
> **Scope:** SQLite → PostgreSQL  
> **Project:** MemoryChat  
> **Deployment target:** Railway  
> **Local development:** Docker Compose  
> **Production database:** Managed PostgreSQL  
> **Critical rule:** Never delete or overwrite the existing SQLite database until backup, schema validation, migration verification, and rollback checks have passed.

---

# 0. Executive Summary

MemoryChat currently uses SQLite during development and needs to move to PostgreSQL before production deployment.

The current project already uses Alembic migrations and has PostgreSQL support through `psycopg2-binary`. The existing migration proposal also identifies Docker Compose as the intended PostgreSQL development environment.

The migration should **not** simply change:

```env
DATABASE_URL=sqlite:///./data/app.db
```

to:

```env
DATABASE_URL=postgresql://...
```

and assume everything works.

The correct migration is:

```text
AUDIT
  ↓
BACKUP SQLite
  ↓
VERIFY Alembic
  ↓
START PostgreSQL
  ↓
CREATE PostgreSQL SCHEMA
  ↓
MIGRATE / REBUILD DATA
  ↓
VERIFY DATA INTEGRITY
  ↓
RUN APPLICATION TESTS
  ↓
RUN INTEGRATION TESTS
  ↓
SWITCH DEVELOPMENT DEFAULT TO PostgreSQL
  ↓
VALIDATE DOCKER
  ↓
PREPARE RAILWAY PostgreSQL
  ↓
PRODUCTION MIGRATION
  ↓
VERIFY
  ↓
DEPRECATE SQLite
```

The goal is not merely "make PostgreSQL work".

The goal is:

> **Make PostgreSQL the authoritative production database while preserving application behavior, data integrity, migrations, security, testability, and rollback capability.**

---

# 1. User Review Required

## Decision A — Existing SQLite data

Default recommendation:

> **Preserve and migrate existing SQLite data unless it is explicitly confirmed to be disposable.**

Even if the project is pre-production, the agent must not assume that `data/app.db` is disposable.

If the user confirms that the SQLite database contains only throwaway development data, a fresh PostgreSQL database may be used.

Otherwise:

```text
SQLite
  ↓
Backup
  ↓
Migration script
  ↓
PostgreSQL
```

---

## Decision B — Test database

Recommended strategy:

### Unit tests

Keep fast isolated tests where practical.

### Integration/API tests

Prefer PostgreSQL for database-sensitive tests because PostgreSQL will be production.

Recommended:

```text
Unit tests
   ↓
SQLite/in-memory or mocks only where truly appropriate

Integration tests
   ↓
PostgreSQL test database

Production
   ↓
PostgreSQL
```

Do not blindly keep SQLite for tests that verify PostgreSQL-specific behavior.

The agent must identify which tests are database-sensitive before changing the test architecture.

---

# 2. Non-Negotiable Safety Rules

The agent MUST follow these rules.

1. Never delete `data/app.db` before creating and verifying a backup.
2. Never run destructive database commands against production without explicit approval.
3. Never run `DROP DATABASE` against an existing production database.
4. Never run `alembic downgrade` on production as a generic rollback strategy without explicit approval.
5. Never commit database passwords or connection strings containing credentials.
6. Never hardcode PostgreSQL credentials.
7. Never expose `DATABASE_URL` to the frontend.
8. Never assume SQLite and PostgreSQL behave identically.
9. Never silently alter schema semantics to make migrations pass.
10. Never delete existing tests just because they fail after the migration.
11. Never bypass failing migrations by manually creating tables in production.
12. Never mark the migration complete without data-integrity verification.
13. Never switch production traffic until the PostgreSQL health check passes.
14. Keep a rollback/recovery path documented before production cutover.
15. Use separate local, staging, and production credentials.
16. Do not log full database URLs or passwords.
17. Do not modify unrelated features during the database migration.
18. If a destructive action is required, STOP and ask for approval.
19. If repository behavior is uncertain, STOP and inspect the code rather than guessing.
20. PostgreSQL must become the source of truth before SQLite is removed.

---

# 3. Target Architecture

## Local development

```text
Developer Machine
       │
       ▼
Docker Compose
       │
       ├── FastAPI
       │
       ├── Next.js
       │
       └── PostgreSQL
             │
             └── postgres_data volume
```

Recommended:

```text
DATABASE_URL=postgresql://...
```

for normal development after migration.

---

## Testing

```text
Test Runner
     │
     ├── Unit tests
     │
     └── Integration tests
              │
              ▼
        PostgreSQL Test DB
```

---

## Production

```text
Internet
    │
    ▼
Railway
    │
    ├── Next.js
    │
    └── FastAPI
           │
           ▼
      Railway PostgreSQL
```

The frontend must never connect directly to PostgreSQL.

Correct:

```text
Browser → FastAPI → PostgreSQL
```

Incorrect:

```text
Browser → PostgreSQL
```

---

# 4. Phase 1 — Repository & Database Audit

Before modifying anything, inspect the repository.

## Backend

Identify:

- SQLAlchemy engine configuration
- session factory
- database dependency
- model definitions
- repositories
- services
- raw SQL
- transactions
- connection pooling
- startup initialization
- database health checks

## Configuration

Inspect:

- `.env`
- `.env.example`
- `requirements.txt`
- `pyproject.toml`
- `alembic.ini`
- `alembic/env.py`
- `docker-compose.yml`
- Dockerfiles
- Railway configuration
- CI configuration

## Database

Inspect:

```text
data/app.db
```

Determine:

- file size
- tables
- schema
- row counts
- indexes
- foreign keys
- constraints
- SQLite-specific features

## Tests

Find all tests that use:

```text
sqlite://
sqlite:///:memory:
data/app.db
```

Classify them:

```text
Unit
Integration
API
E2E
Migration
Repository
Service
```

---

## Required audit report

Before implementation, the agent must report:

```text
1. Current database URL configuration
2. SQLAlchemy configuration
3. Alembic configuration
4. Existing migrations
5. Current SQLite schema
6. Current table list
7. Row counts
8. Foreign keys
9. Indexes
10. SQLite-specific SQL/features
11. Existing PostgreSQL support
12. Tests using SQLite
13. Docker configuration
14. Railway readiness
15. Data migration complexity
16. Risks
```

Then STOP for approval if unexpected schema/data issues are found.

---

# 5. Phase 2 — SQLite Backup

Before changing the database:

Create a verified backup.

At minimum preserve:

```text
data/app.db
```

Prefer creating an explicit backup:

```text
data/backups/app-YYYYMMDD-HHMMSS.db
```

Also record:

```text
file size
checksum
timestamp
```

Example checksum:

```bash
sha256sum data/app.db
```

On Windows PowerShell:

```powershell
Get-FileHash data/app.db -Algorithm SHA256
```

The agent must verify that the backup can actually be opened/read.

Do not proceed if the backup is missing or corrupt.

---

# 6. Phase 3 — PostgreSQL Docker Service

Modify `docker-compose.yml`.

Conceptually:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: memorychat
      POSTGRES_USER: memorychat
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U memorychat -d memorychat"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  postgres_data:
```

The exact PostgreSQL version must be chosen based on:

- current project dependencies
- Railway supported versions
- compatibility with SQLAlchemy/driver
- production target

Do not blindly change versions if the repository already specifies one.

---

# 7. Phase 4 — Docker Networking

When backend runs inside Docker:

```text
backend
   │
   ▼
postgres:5432
```

The backend should use the Docker service name:

```text
postgres
```

not:

```text
localhost
```

Example:

```env
DATABASE_URL=postgresql://memorychat:password@postgres:5432/memorychat
```

When backend runs directly on the host:

```text
DATABASE_URL=postgresql://memorychat:password@localhost:5432/memorychat
```

Do not use the same connection string blindly in both environments.

---

# 8. Phase 5 — Environment Configuration

Update:

```text
.env
.env.example
```

Recommended structure:

```env
DATABASE_URL=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=
```

Only define variables that the current project actually needs.

## `.env.example`

Must contain placeholders only:

```env
DATABASE_URL=postgresql://memorychat:CHANGE_ME@localhost:5432/memorychat
```

Never place real credentials in `.env.example`.

---

# 9. Phase 6 — PostgreSQL Driver

Verify PostgreSQL support.

The existing project mentions:

```text
psycopg2-binary
```

The agent must inspect the actual dependency configuration before modifying it.

Do not add a second PostgreSQL driver unnecessarily.

If the project already uses a compatible driver:

```text
Keep it.
```

If not:

```text
Add the required driver.
```

Then run the dependency installation and application import checks.

---

# 10. Phase 7 — Alembic Audit

This is one of the most important phases.

Inspect:

```text
alembic.ini
alembic/env.py
alembic/versions/*
```

Determine:

- current migration head
- migration ordering
- metadata configuration
- naming conventions
- SQLite-specific migration logic
- PostgreSQL compatibility
- enum handling
- UUID handling
- timestamps
- JSON columns
- foreign keys
- indexes
- unique constraints

Run against a fresh PostgreSQL database:

```bash
alembic upgrade head
```

The migration must work from an empty database.

---

# 11. Phase 8 — Fresh PostgreSQL Schema Test

Create a completely fresh PostgreSQL database.

Run:

```bash
alembic upgrade head
```

Then inspect:

```text
tables
columns
types
primary keys
foreign keys
unique constraints
indexes
```

Compare against SQLAlchemy models.

Do not manually create missing tables to make the application start.

If Alembic is wrong:

```text
Fix migration
    ↓
Reset test PostgreSQL DB
    ↓
alembic upgrade head
    ↓
Verify again
```

---

# 12. Phase 9 — SQLite Schema Inventory

Before migrating data, generate an inventory:

```text
Table                Rows
--------------------------
users                N
conversations        N
participants         N
messages             N
connection_requests  N
...
```

Also record:

```text
NULL counts
duplicate candidates
foreign-key violations
orphan records
```

The exact tables must come from the actual repository.

---

# 13. Phase 10 — Data Migration Strategy

Choose one strategy based on audit results.

## Strategy A — Fresh start

Allowed only if the user explicitly confirms existing SQLite data is disposable.

```text
SQLite
   X
   ↓
Fresh PostgreSQL
```

## Strategy B — Data migration

If data matters:

```text
SQLite
   ↓
Extract
   ↓
Transform
   ↓
PostgreSQL
   ↓
Validate
```

Use a dedicated migration script.

Possible approaches:

```text
Python + SQLAlchemy
pgloader
```

The agent must choose based on actual schema complexity.

Do not introduce `pgloader` simply because it was mentioned in an old plan.

---

# 14. Phase 11 — Data Type Compatibility

The agent must explicitly inspect differences between SQLite and PostgreSQL.

Common areas:

```text
SQLite                  PostgreSQL
-------------------------------------------
INTEGER                 INTEGER/BIGINT
TEXT                    TEXT/VARCHAR
REAL                    DOUBLE PRECISION
BOOLEAN emulation       BOOLEAN
JSON/text               JSONB/JSON
timestamps              TIMESTAMP/TIMESTAMPTZ
UUID stored as text     UUID
autoincrement           IDENTITY/SERIAL
```

Do not automatically convert types.

Use the project's actual SQLAlchemy models and API contracts as the source of truth.

---

# 15. Phase 12 — UUID and ID Validation

MemoryChat uses entity IDs throughout:

```text
users
conversations
messages
connection requests
participants
```

Verify:

- Python type
- SQLAlchemy type
- PostgreSQL column type
- API serialization
- foreign key type compatibility

A foreign key must match the referenced primary key semantics.

---

# 16. Phase 13 — Timestamp Validation

Inspect all timestamp fields.

Verify:

```text
created_at
updated_at
deleted_at
expires_at
```

Check:

- timezone behavior
- UTC assumptions
- serialization
- comparison
- pagination ordering
- WebSocket event timestamps

This is especially important because MemoryChat already uses timestamp + ID ordering for cursor pagination.

---

# 17. Phase 14 — Constraints and Indexes

PostgreSQL must preserve or improve:

- primary keys
- foreign keys
- unique constraints
- check constraints
- indexes

Pay particular attention to:

```text
conversation_id
created_at
client_message_id
deleted_at
user_id
sender_user_id
```

Only create indexes justified by actual query patterns.

Avoid blindly adding indexes to every column.

After migration, inspect query plans for important queries.

---

# 18. Phase 15 — Transaction Semantics

Review operations that depend on multiple writes.

Examples:

```text
Send message
Create conversation
Accept connection request
Recall message
Recommendation acceptance
Memory updates
```

Verify that PostgreSQL transactions preserve atomic behavior.

Do not assume SQLite transaction behavior is identical.

---

# 19. Phase 16 — Connection Pooling

Review SQLAlchemy engine configuration.

Production should use an appropriate connection pool.

Do not blindly set large pool sizes.

Railway PostgreSQL has finite connection capacity.

Configure conservatively based on:

```text
Railway database limits
number of backend replicas
expected concurrent users
```

If multiple backend instances are later deployed:

```text
total DB connections
=
pool_size × instance_count
```

must remain within safe limits.

---

# 20. Phase 17 — Database Health Check

Implement/verify a database health check.

Conceptually:

```text
GET /health
       │
       ├── application
       └── PostgreSQL connectivity
```

Do not expose sensitive database information.

Healthy response:

```json
{
  "status": "ok"
}
```

Detailed database errors belong in server logs, not public API responses.

---

# 21. Phase 18 — Test Database Strategy

Recommended:

```text
Unit
 └── isolated mocks/in-memory where appropriate

Integration
 └── PostgreSQL test database

E2E
 └── PostgreSQL environment
```

Create an isolated test database:

```text
memorychat_test
```

Never point automated tests at production.

Never use:

```text
DROP DATABASE memorychat
```

against a shared environment.

---

# 22. Phase 19 — Test Suite Migration

Update tests that assume SQLite behavior.

Do not rewrite all tests blindly.

Prioritize:

```text
repositories
services
API
database transactions
pagination
message recall
connection requests
WebSockets
AI memory persistence
```

Run:

```bash
pytest
```

Then:

```bash
npm run lint
npm run typecheck
```

The database migration is not complete while core tests are failing.

---

# 23. Phase 20 — PostgreSQL Integration Verification

Test complete flows:

### Authentication

```text
Register
  ↓
PostgreSQL
  ↓
Login
  ↓
JWT
```

### Connection requests

```text
Send
Accept
Reject
Cancel
```

### Chat

```text
Create/open conversation
  ↓
Send message
  ↓
Persist
  ↓
WebSocket
```

### Recall

```text
Recall message
  ↓
deleted_at
  ↓
WebSocket
  ↓
Receiver updates
```

### Cursor pagination

```text
Newest messages
  ↓
before_created_at
+
before_id
  ↓
Older messages
```

---

# 24. Phase 21 — Data Integrity Verification

If existing SQLite data was migrated, compare:

```text
SQLite source
     VS
PostgreSQL target
```

At minimum:

```text
table counts
important IDs
foreign keys
unique constraints
message counts
conversation counts
user counts
connection request counts
```

For critical tables, compare row-level identifiers.

Do not rely only on total row counts.

Example:

```text
SQLite users:
100

PostgreSQL users:
100

```

is not enough.

Also verify:

```text
same IDs
same relationships
same important values
```

---

# 25. Phase 22 — Application Behavior Verification

Start the application against PostgreSQL.

Verify:

```text
[ ] Register
[ ] Login
[ ] Logout
[ ] Create/open chat
[ ] Send message
[ ] Receive message
[ ] Recall message
[ ] Connection request
[ ] Accept request
[ ] Reject request
[ ] Cancel request
[ ] AI search
[ ] AI memory
[ ] Copilot
[ ] Recommendations
[ ] WebSocket reconnect
[ ] Cursor pagination
```

The exact list should be adapted to the actual implemented features.

---

# 26. Phase 23 — Docker Full Stack Verification

Run the complete local stack:

```bash
docker compose up -d
```

Then verify:

```text
postgres healthy
      ↓
backend healthy
      ↓
frontend healthy
```

Inspect:

```bash
docker compose ps
docker compose logs backend
docker compose logs postgres
```

No critical startup errors should remain.

---

# 27. Phase 24 — PostgreSQL Persistence Test

Restart the PostgreSQL container:

```bash
docker compose restart postgres
```

Verify that data remains.

Then test:

```text
create data
 ↓
restart postgres
 ↓
read data
```

This validates the Docker volume.

Never treat container filesystem storage as production persistence.

---

# 28. Phase 25 — Backup and Restore

Define a PostgreSQL backup strategy before production.

At minimum understand:

```text
pg_dump
pg_restore
```

Example conceptual backup:

```bash
pg_dump "$DATABASE_URL" > backup.sql
```

The exact command must be adapted to the deployed PostgreSQL environment.

A backup is not sufficient unless restore is tested.

Recommended:

```text
Backup
  ↓
Restore into isolated DB
  ↓
Run integrity checks
```

---

# 29. Phase 26 — Railway PostgreSQL Preparation

Before production deployment, provision PostgreSQL on Railway.

Configure:

```text
DATABASE_URL
```

using Railway's managed PostgreSQL connection details.

Do not manually paste production credentials into source code.

The backend should receive the connection string through Railway environment variables.

---

# 30. Phase 27 — Railway Migration

The production migration should follow:

```text
Railway PostgreSQL
       ↓
Connection test
       ↓
alembic upgrade head
       ↓
Schema verification
       ↓
Data migration if required
       ↓
Data verification
       ↓
Backend deployment
```

Do not start the backend against an unknown schema.

---

# 31. Phase 28 — Production Migration Safety

Before production migration:

```text
[ ] SQLite/source backup exists
[ ] PostgreSQL backup/recovery strategy exists
[ ] Alembic upgrade tested on clean DB
[ ] Migration tested on staging
[ ] Data counts verified
[ ] Application tests pass
[ ] Rollback/recovery documented
[ ] Production credentials configured
[ ] No destructive command is pending
```

If any critical item fails:

```text
STOP
```

---

# 32. Phase 29 — Production Smoke Test

After Railway deployment:

```text
Health
 ↓
Database
 ↓
Authentication
 ↓
Chat
 ↓
WebSocket
 ↓
Connection requests
 ↓
Message recall
 ↓
AI/RAG
```

Check server logs for:

```text
database connection errors
transaction errors
timeout errors
pool exhaustion
migration errors
```

---

# 33. Phase 30 — SQLite Deprecation

Do not remove SQLite immediately.

For a stabilization period:

```text
PostgreSQL = primary
SQLite = archived/recovery source
```

Once PostgreSQL is proven stable:

Remove:

```text
SQLite runtime dependency
SQLite startup logic
SQLite Docker/service references
obsolete SQLite tests
obsolete SQLite documentation
```

Keep the archived backup outside the application runtime.

---

# 34. Rollback Strategy

There are two different rollback scenarios.

## Before production cutover

Easy rollback:

```text
PostgreSQL migration fails
        ↓
Do not switch application
        ↓
Fix migration
```

SQLite remains intact.

## After production cutover

Do not assume that switching `DATABASE_URL` back to SQLite is safe.

If production PostgreSQL contains new data:

```text
PostgreSQL
    ↓
contains new writes
```

cannot simply be replaced with an old SQLite snapshot without data loss.

Therefore the preferred production recovery strategy is:

```text
Fix PostgreSQL
OR
restore PostgreSQL backup
OR
forward-fix migration
```

SQLite should be considered an emergency historical backup, not an automatic production rollback target.

---

# 35. Agent Execution Protocol

The agent MUST execute in this order:

```text
AUDIT
  ↓
BACKUP
  ↓
POSTGRES DOCKER
  ↓
ALEMBIC VALIDATION
  ↓
SCHEMA VALIDATION
  ↓
DATA MIGRATION STRATEGY
  ↓
IMPLEMENT
  ↓
TEST
  ↓
DATA INTEGRITY CHECK
  ↓
FULL STACK TEST
  ↓
RAILWAY STAGING
  ↓
PRODUCTION DATABASE
  ↓
PRODUCTION MIGRATION
  ↓
SMOKE TEST
  ↓
STABILITY PERIOD
  ↓
DEPRECATE SQLITE
```

---

# 36. Agent Stop Conditions

The agent MUST STOP and ask for approval if:

- SQLite contains unexpected important data.
- Schema mismatch is discovered.
- Alembic migration requires destructive changes.
- Existing production data is detected.
- A migration would drop/rename important columns.
- PostgreSQL type conversion may lose information.
- A test requires changing application semantics.
- A production database reset appears necessary.
- Rollback is unclear.
- Data counts do not match unexpectedly.
- Foreign-key relationships are broken.
- Authentication data is affected.
- Any secret is discovered in the repository.

---

# 37. Documentation Updates

After completion, update the project's documentation appropriately.

Recommended:

### `ARCHITECTURE.md`

Document:

```text
PostgreSQL
SQLAlchemy
Alembic
connection pooling
database boundaries
```

### `DECISIONS.md`

Record:

```text
Decision:
SQLite → PostgreSQL

Reason:
Production reliability,
concurrency,
transaction semantics,
Railway compatibility,
and scalability.
```

### `long-term.md`

Record only durable project-level decisions that future agents need to know.

### `WORKLOG.md`

Record:

```text
migration date
what changed
tests
issues
verification
```

### `.env.example`

Document required PostgreSQL variables without secrets.

Do not duplicate the entire migration plan into every documentation file.

---

# 38. Final Verification Checklist

## Database

```text
[ ] PostgreSQL running
[ ] Correct PostgreSQL version
[ ] Alembic upgrade head succeeds
[ ] Schema verified
[ ] Foreign keys verified
[ ] Indexes verified
[ ] Constraints verified
[ ] Connection pool configured
```

## Data

```text
[ ] SQLite backup created
[ ] Backup verified
[ ] Data migration completed if required
[ ] Row counts verified
[ ] IDs verified
[ ] Relationships verified
[ ] No unexpected data loss
```

## Application

```text
[ ] Backend starts
[ ] Frontend starts
[ ] Register works
[ ] Login works
[ ] Chat works
[ ] WebSocket works
[ ] Message recall works
[ ] Connection requests work
[ ] Cursor pagination works
[ ] AI/RAG works
```

## Testing

```text
[ ] pytest passes
[ ] Integration tests pass
[ ] npm run lint passes
[ ] npm run typecheck passes
[ ] Critical Playwright flows pass
```

## Deployment

```text
[ ] Railway PostgreSQL configured
[ ] Production DATABASE_URL secret
[ ] Alembic production migration verified
[ ] Production health check passes
[ ] Production smoke test passes
[ ] Monitoring/logging checked
```

## Recovery

```text
[ ] PostgreSQL backup strategy documented
[ ] Restore tested
[ ] Migration rollback/recovery documented
[ ] SQLite backup archived
```

---

# 39. Final Objective

After completion, MemoryChat should have:

```text
                 MemoryChat
                     │
                     ▼
                  FastAPI
                     │
                     ▼
                PostgreSQL
              source of truth
```

with:

```text
Local:
Docker PostgreSQL

Staging:
Managed PostgreSQL / isolated environment

Production:
Railway PostgreSQL
```

SQLite should no longer be required by the production application.

The final state must preserve:

- users
- authentication
- conversations
- participants
- messages
- message recall
- connection requests
- WebSockets
- cursor pagination
- AI memory
- Copilot
- recommendations
- RAG
- application security

The migration is considered complete only when PostgreSQL is the verified source of truth, the application behaves correctly against PostgreSQL, the deployment environment is validated, and a tested recovery strategy exists.

> **Primary principle:** Do not optimize for "migration completed". Optimize for **data safety + production correctness + recoverability**.
