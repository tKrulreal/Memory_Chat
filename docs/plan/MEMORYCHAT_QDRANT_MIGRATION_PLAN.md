# MEMORYCHAT_QDRANT_MIGRATION_PLAN.md

# MemoryChat — ChromaDB → Qdrant Migration Plan

## Context

The entire `MEMORYCHAT_PRE_DEPLOYMENT_PLAN.md` has already been completed.

MemoryChat currently uses ChromaDB for AI/RAG vector storage. The goal is to replace ChromaDB with Qdrant **before Railway production deployment**, while preserving existing AI behavior and avoiding unrelated architectural changes.

```text
Current:
MemoryChat → AI/RAG → ChromaDB

Target:
MemoryChat → AI/RAG → Qdrant
```

---

# 1. Migration Principles

1. Inspect the current implementation before changing anything.
2. Do not assume how ChromaDB is currently used.
3. Do not rewrite unrelated AI/RAG logic.
4. Preserve the current embedding model unless explicitly approved otherwise.
5. Preserve metadata semantics and user/conversation isolation.
6. Do not delete ChromaDB data until Qdrant has been verified.
7. Keep the migration reversible until validation is complete.
8. Never commit Qdrant credentials.
9. Use environment-based configuration.
10. Update architecture/deployment documentation after migration.

---

# Phase 1 — Audit Current ChromaDB Usage

Inspect every ChromaDB integration point:

- client initialization
- collection creation
- collection naming
- embedding generation
- document insertion/update/deletion
- similarity search
- metadata filtering
- score/distance handling
- persistence path
- startup initialization
- background workers
- AI agents
- RAG services
- memory services
- tests
- environment variables
- Docker configuration
- Railway configuration

Search for:

```text
chromadb
ChromaDB
chromadb.Client
PersistentClient
HttpClient
collection
embedding
similarity
vector
RAG
memory
```

### Output

Produce:

| Component | Current ChromaDB Usage | Qdrant Replacement | Risk |
|---|---|---|---|

Do not modify code during this phase.

---

# Phase 2 — Define Target Qdrant Architecture

Prefer the following structure when compatible with the existing project:

```text
AI / RAG
   ↓
Vector Store Interface
   ↓
Qdrant Repository
   ↓
Qdrant
```

If the project already has a vector-store abstraction, reuse it.

Do not introduce unnecessary abstraction layers.

---

# Phase 3 — Map ChromaDB to Qdrant

Create an explicit mapping:

| ChromaDB | Qdrant |
|---|---|
| Collection | Collection |
| Document ID | Point ID |
| Embedding | Vector |
| Metadata | Payload |
| `add()` | `upsert()` |
| `update()` | `upsert()` |
| `delete()` | Delete points |
| `query()` | Qdrant search/query API |
| Metadata filter | Payload filter |
| Persist directory | Qdrant storage |
| Distance metric | Collection distance |

Verify the exact Qdrant client version and API before implementation.

---

# Phase 4 — Embedding Compatibility

Inspect:

- embedding provider
- model
- vector dimension
- distance metric
- normalization
- chunking
- embedding generation code

The Qdrant collection dimension must match the existing embedding dimension.

Do **not** change the embedding model as part of this migration unless explicitly approved.

If the embedding model changes, treat that as a separate migration.

---

# Phase 5 — Metadata and Security Isolation

Identify all metadata currently stored in ChromaDB, for example:

```text
user_id
conversation_id
message_id
document_id
source
created_at
type
```

Use the actual repository fields.

Map them to Qdrant payloads.

Verify every retrieval query preserves existing:

- user isolation
- conversation isolation
- authorization rules

A user must never retrieve vectors belonging to another user or conversation.

This is a security-critical requirement.

---

# Phase 6 — Implement Qdrant Integration

Implement a Qdrant adapter following the current architecture.

Preferred responsibility:

```text
QdrantVectorStore
```

It should handle:

- collection initialization
- upsert
- delete
- similarity search
- payload filtering
- health checks
- collection information

Keep business logic outside the vector-store adapter.

Do not modify frontend behavior unless an API contract actually requires it.

---

# Phase 7 — Configuration

Replace ChromaDB-specific configuration with Qdrant configuration.

Potential variables:

```text
QDRANT_URL
QDRANT_API_KEY
QDRANT_COLLECTION
```

Only use variables actually required by the chosen deployment.

Update:

- backend settings
- `.env.example`
- Docker configuration
- Railway deployment documentation

Keep real credentials out of Git.

Remove old ChromaDB variables only after migration is completely verified.

---

# Phase 8 — Local Qdrant Environment

Provide a reproducible local Qdrant setup, preferably through Docker.

Target:

```text
Docker Compose
│
├── frontend
├── backend
├── postgres
└── qdrant
```

Verify:

- Qdrant starts
- backend connects
- collection is created
- vectors can be inserted
- vectors can be queried
- metadata filters work
- vectors can be deleted
- persistence survives restart

---

# Phase 9 — Data Migration Strategy

Determine whether existing ChromaDB vectors must be migrated.

## Preferred: Re-index from source data

If source data remains available:

```text
PostgreSQL / Source Data
          ↓
       Chunking
          ↓
      Embeddings
          ↓
        Qdrant
```

This is preferred because it avoids dependence on ChromaDB internals.

## Alternative: Export ChromaDB

Only use if re-indexing is impractical:

```text
ChromaDB
   ↓
Export
   ↓
Transform
   ↓
Qdrant
```

Do not delete ChromaDB before the Qdrant index is validated.

Document which strategy is selected and why.

---

# Phase 10 — Qdrant Collection Initialization

Make collection initialization idempotent.

The application must safely handle:

- collection missing
- collection already exists
- empty collection
- populated collection

Do not recreate the collection on every startup.

Verify:

- vector dimension
- distance metric
- collection name
- payload indexes if required
- collection health

---

# Phase 11 — RAG Retrieval Validation

Compare representative retrieval behavior.

For each test query evaluate:

```text
Query
 ↓
Embedding
 ↓
Top-K results
 ↓
Metadata filters
 ↓
Scores
 ↓
Final context
```

Verify:

- relevant results
- correct ordering
- metadata filters
- user isolation
- conversation isolation
- deleted/invalid content handling
- empty-result behavior

Do not require identical numeric scores between databases. Require semantic and functional equivalence.

---

# Phase 12 — Automated Tests

Add/update:

## Unit tests

- Qdrant repository
- initialization
- upsert
- delete
- search
- payload filtering
- configuration

## Integration tests

Run against a real Qdrant instance:

- insert
- search
- filter
- delete
- restart persistence

## RAG tests

Verify:

- retrieval
- context construction
- authorization boundaries
- empty results
- multiple users
- multiple conversations

Run:

```bash
pytest
npm run lint
npm run typecheck
```

---

# Phase 13 — Performance Validation

Measure:

- embedding generation time
- vector insertion latency
- search latency
- top-K retrieval latency
- memory usage
- startup time

Compare Qdrant with the current ChromaDB baseline where practical.

Record:

| Metric | ChromaDB | Qdrant | Difference | Acceptable? |
|---|---:|---:|---:|---|

Do not optimize prematurely.

---

# Phase 14 — Railway Qdrant Deployment

Evaluate two deployment models.

## Option A — Qdrant Cloud

```text
Railway Backend
      │
      ▼
Qdrant Cloud
```

## Option B — Qdrant on Railway

```text
Railway
│
├── Frontend
├── Backend
├── PostgreSQL
└── Qdrant + Persistent Volume
```

Choose based on:

- cost
- persistence
- backups
- latency
- credentials
- operational complexity
- current application scale

Do not expose Qdrant publicly without authentication/network controls.

---

# Phase 15 — Persistence and Recovery

Determine where Qdrant data physically lives.

If self-hosted:

```text
Qdrant
  ↓
Railway Volume
  ↓
Persistent vector data
```

Do not rely on ephemeral container storage.

Document:

- backup strategy
- restore strategy
- rebuild strategy
- collection recovery
- whether vectors can be rebuilt from PostgreSQL/source data

---

# Phase 16 — Remove ChromaDB

Only remove ChromaDB after all of these pass:

- Qdrant integration
- tests
- RAG validation
- authorization validation
- performance validation
- staging deployment
- data migration/re-indexing
- backup/rebuild strategy

Then remove:

- ChromaDB dependencies
- ChromaDB configuration
- ChromaDB Docker services
- obsolete ChromaDB code
- obsolete tests
- obsolete documentation

Do not remove ChromaDB prematurely.

---

# Phase 17 — Documentation and Decisions

Update:

- `ARCHITECTURE.md`
- `DECISIONS.md`
- `long-term.md`
- `WORKLOG.md`
- Railway deployment documentation

Record:

1. Why ChromaDB was replaced.
2. Why Qdrant was selected.
3. Qdrant deployment model.
4. Collection design.
5. Embedding model/dimension.
6. Payload schema.
7. Retrieval strategy.
8. Persistence.
9. Backup/rebuild strategy.
10. Operational considerations.

Avoid duplicating the same information across documents.

---

# Phase 18 — Final Verification

Run:

```bash
pytest
npm run lint
npm run typecheck
```

Also verify:

- Docker production builds
- AI Hub
- Copilot
- Recommendations
- Search
- RAG/memory
- user isolation
- conversation isolation
- unauthorized retrieval rejection
- Qdrant credential protection
- no secret leakage

Ensure Qdrant migration does not break:

- WebSocket
- message events
- message recall
- connection requests

---

# Phase 19 — Railway Integration

Update the existing Railway deployment architecture.

Target:

```text
                         Railway
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
      Next.js            FastAPI          PostgreSQL
                            │
                            ▼
                         AI / RAG
                            │
                            ▼
                          Qdrant
```

If Qdrant Cloud is selected:

```text
Railway
│
├── Next.js
├── FastAPI
└── PostgreSQL
       │
       ▼
Qdrant Cloud
```

Update:

- Railway services
- Railway variables
- Docker Compose
- deployment documentation
- health checks
- staging tests

---

# Phase 20 — Production Release Gate

Do not release until all are true:

```text
ChromaDB dependencies removed        ✅
Qdrant integration complete          ✅
Collection initialized correctly     ✅
Embeddings compatible                ✅
Metadata mapped correctly            ✅
User isolation verified              ✅
Conversation isolation verified      ✅
Migration/re-indexing verified       ✅
RAG retrieval verified               ✅
Integration tests pass               ✅
Backend tests pass                   ✅
Frontend lint/typecheck pass         ✅
Docker build passes                  ✅
Railway staging works                ✅
Persistent storage verified          ✅
Backup/rebuild strategy documented   ✅
Production configuration ready       ✅
```

---

# Required Documentation

Create:

`MEMORYCHAT_QDRANT_MIGRATION.md`

It must contain:

1. Migration overview
2. Current ChromaDB architecture
3. Target Qdrant architecture
4. ChromaDB → Qdrant mapping
5. Embedding compatibility
6. Payload/metadata mapping
7. Collection design
8. Migration/re-indexing strategy
9. Testing strategy
10. Performance results
11. Railway deployment model
12. Persistence
13. Backup/recovery
14. Rollback plan
15. ChromaDB removal checklist
16. Final verification

---

# Execution Rules

## First step

Do **NOT** immediately modify code.

First inspect the repository and report:

1. Every ChromaDB integration point.
2. Current vector schema.
3. Current embedding model and dimension.
4. Current metadata/payload.
5. Current retrieval/filter logic.
6. Current persistence model.
7. Current AI/RAG dependencies.
8. Existing tests.
9. Existing Docker/Railway configuration.
10. Recommended Qdrant architecture.

Then STOP and wait for approval.

## During implementation

- Make small, isolated changes.
- Follow existing architecture.
- Preserve current AI behavior.
- Do not change embedding models unless explicitly approved.
- Do not delete ChromaDB data until migration is verified.
- Do not expose Qdrant credentials.
- Do not modify unrelated frontend features.
- Run tests after each major migration step.
- Use `architect`, `rag-pipeline-reviewer`, `database-reviewer`, `security-reviewer`, and `code-reviewer` where appropriate.

---

# Success Criteria

The final architecture should be:

```text
Private GitHub
      ↓
Railway
      │
      ├── Next.js
      │
      ├── FastAPI
      │      │
      │      └── AI / RAG
      │              │
      │              ▼
      │           Qdrant
      │
      └── PostgreSQL
```

The migration is complete only when MemoryChat no longer depends on ChromaDB and all existing AI/RAG functionality works correctly with Qdrant.

**Objective: replace ChromaDB with Qdrant safely, preserve current behavior, verify retrieval/security/persistence, and integrate the result into the Railway production architecture.**
