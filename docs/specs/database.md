# DATABASE.md — Database Design & Schema

## MemoryChat MVP v1.0

---

## 1. Database Architecture

### 1.1 Polyglot Persistence Strategy

MemoryChat uses different databases for different data types based on their characteristics:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA TYPE → DATABASE MAPPING                       │
│                                                                       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Transactional │    │    Vector       │    │    Graph        │ │
│  │   (Users, msgs) │    │   (Embeddings)  │    │  (Relationships│ │
│  │        │        │    │        │        │    │        │        │ │
│  │        ▼        │    │        ▼        │    │        ▼        │ │
│  │   PostgreSQL    │    │     Qdrant       │    │     Neo4j       │ │
│  │   (Future)      │    │    (Future)      │    │   (Future)      │ │
│  │        │        │    │        │        │    │                 │ │
│  │        ▼        │    │        ▼        │    │                 │ │
│  │     SQLite      │    │    ChromaDB      │    │                 │ │
│  │   (MVP)        │    │    (MVP)        │    │                 │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│                                                                       │
│  ┌─────────────────┐    ┌─────────────────┐                        │
│  │     Cache       │    │     Session      │                        │
│  │   (Context)     │    │    (JWT)        │                        │
│  │        │        │    │        │        │                        │
│  │        ▼        │    │        ▼        │                        │
│  │   In-Memory     │    │   JWT Token      │                        │
│  │    (MVP)        │    │                 │                        │
│  │        │        │    │        ▼        │                        │
│  │        ▼        │    │     Redis       │                        │
│  │     Redis       │    │   (Future)       │                        │
│  │   (Future)      │    │                 │                        │
│  └─────────────────┘    └─────────────────┘                        │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Migration Path

| MVP | Phase 2 | Phase 3 |
|-----|--------|---------|
| SQLite | PostgreSQL | PostgreSQL + Read Replicas |
| ChromaDB | Qdrant | Qdrant Cluster |
| — | Neo4j | Neo4j Cluster |
| In-Memory | Redis | Redis Cluster |

---

## 2. Entity Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           ENTITY RELATIONSHIP DIAGRAM                         │
│                                                                              │
│    ┌──────────────┐                                                          │
│    │     USER     │                                                          │
│    │──────────────│                                                          │
│    │ id (PK)      │                                                          │
│    │ email        │                                                          │
│    │ password_hash│                                                          │
│    │ full_name    │                                                          │
│    │ avatar       │                                                          │
│    │ created_at   │                                                          │
│    │ updated_at   │                                                          │
│    └──────┬───────┘                                                          │
│           │                                                                  │
│           │ 1:N                                                               │
│           │                                                                  │
│           ├──────────────────────────────────┐                               │
│           │                                  │                               │
│           ▼                                  ▼                               │
│  ┌─────────────────────┐          ┌─────────────────────┐                   │
│  │      CONTACT       │          │    CONVERSATION     │                   │
│  │────────────────────│          │────────────────────│                   │
│  │ id (PK)            │          │ id (PK)            │                   │
│  │ user_id (FK)       │          │ user_id (FK)       │                   │
│  │ display_name       │          │ contact_id (FK)    │                   │
│  │ avatar             │          │ last_message       │                   │
│  │ phone              │          │ last_message_time  │                   │
│  │ email              │          │ created_at         │                   │
│  │ created_at         │          │ updated_at         │                   │
│  │ updated_at         │          └─────────┬───────────┘                   │
│  └─────────┬───────────┘                    │                              │
│            │                                 │ 1:N                           │
│            │ 1:1                             │                              │
│            │                                 ▼                              │
│            │                   ┌─────────────────────┐                      │
│            │                   │      MESSAGE        │                      │
│            │                   │────────────────────│                      │
│            │                   │ id (PK)             │                      │
│            │                   │ conversation_id(FK) │                      │
│            │                   │ sender_type         │                      │
│            │                   │ content             │                      │
│            │                   │ message_type        │                      │
│            │                   │ created_at          │                      │
│            │                   └─────────────────────┘                      │
│            │                                                                  │
│            │ 1:1                                                                   │
│            ▼                                                                         │
│  ┌─────────────────────┐                                                           │
│  │   CONTACT_MEMORY   │                                                           │
│  │────────────────────│                                                           │
│  │ id (PK)            │                                                           │
│  │ contact_id (FK)     │                                                           │
│  │ summary             │                                                           │
│  │ profession          │                                                           │
│  │ company             │                                                           │
│  │ skills (JSON)       │                                                           │
│  │ interests (JSON)     │                                                           │
│  │ timeline (JSON)     │                                                           │
│  │ relationship_score   │                                                           │
│  │ last_discussion      │                                                           │
│  │ updated_at           │                                                           │
│  └─────────────────────┘                                                           │
│                                                                              │
│    ┌──────────────┐     N:N     ┌──────────────┐                              │
│    │    CONTACT    │────────────│      TAG      │                              │
│    │──────────────│            │──────────────│                              │
│    │ id (PK)      │            │ id (PK)      │                              │
│    │              │            │ name         │                              │
│    │              │            │ color        │                              │
│    │              │            │ created_at   │                              │
│    └──────────────┘            └──────────────┘                              │
│                                                                              │
│    ┌─────────────────────┐                                                    │
│    │   RECOMMENDATION    │                                                    │
│    │────────────────────│                                                    │
│    │ id (PK)            │◄───────── FK to CONTACT                            │
│    │ contact_id (FK)    │                                                    │
│    │ type               │                                                    │
│    │ reason             │                                                    │
│    │ priority           │                                                    │
│    │ status             │                                                    │
│    │ created_at         │                                                    │
│    └─────────────────────┘                                                    │
│                                                                              │
│    ┌─────────────────────┐                                                    │
│    │     EVENT_LOG       │                                                    │
│    │────────────────────│                                                    │
│    │ id (PK)            │                                                    │
│    │ user_id (FK)       │                                                    │
│    │ conversation_id(FK)│                                                    │
│    │ event_type         │                                                    │
│    │ payload (JSON)     │                                                    │
│    │ created_at         │                                                    │
│    └─────────────────────┘                                                    │
│                                                                              │
│    ┌─────────────────────┐                                                    │
│    │   SEARCH_HISTORY    │                                                    │
│    │────────────────────│                                                    │
│    │ id (PK)            │                                                    │
│    │ user_id (FK)       │                                                    │
│    │ query              │                                                    │
│    │ result_count       │                                                    │
│    │ created_at          │                                                    │
│    └─────────────────────┘                                                    │
│                                                                              │
│    ┌─────────────────────┐                                                    │
│    │    NOTIFICATION     │                                                    │
│    │────────────────────│                                                    │
│    │ id (PK)            │                                                    │
│    │ user_id (FK)       │                                                    │
│    │ type               │                                                    │
│    │ title              │                                                    │
│    │ content            │                                                    │
│    │ status             │                                                    │
│    │ created_at         │                                                    │
│    └─────────────────────┘                                                    │
│                                                                              │
│    ┌─────────────────────┐                                                    │
│    │      SETTING       │                                                    │
│    │────────────────────│                                                    │
│    │ user_id (PK, FK)   │                                                    │
│    │ auto_tag           │                                                    │
│    │ auto_memory        │                                                    │
│    │ theme              │                                                    │
│    │ language           │                                                    │
│    │ notification       │                                                    │
│    └─────────────────────┘                                                    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Table Schemas

### 3.1 User

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    avatar VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

### 3.2 Contact

```sql
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(255) NOT NULL,
    avatar VARCHAR(500),
    phone VARCHAR(50),
    email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure each contact belongs to only one user
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_contacts_user_id ON contacts(user_id);
CREATE INDEX idx_contacts_display_name ON contacts(display_name);
```

### 3.3 Conversation

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    last_message TEXT,
    last_message_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- MVP: 1:1 conversation only
    CONSTRAINT unique_user_contact UNIQUE (user_id, contact_id)
);

-- Indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_contact_id ON conversations(contact_id);
CREATE INDEX idx_conversations_last_message_time ON conversations(last_message_time DESC);
```

### 3.4 Message

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('USER', 'CONTACT')),
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'TEXT' CHECK (message_type IN ('TEXT', 'AI', 'SYSTEM')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
-- Composite for fetching messages in order
CREATE INDEX idx_messages_conv_created ON messages(conversation_id, created_at DESC);
```

### 3.5 ContactMemory

```sql
CREATE TABLE contact_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    summary TEXT,
    profession VARCHAR(255),
    company VARCHAR(255),
    skills JSONB DEFAULT '[]',
    interests JSONB DEFAULT '[]',
    timeline JSONB DEFAULT '[]',
    relationship_score INTEGER DEFAULT 50 CHECK (relationship_score >= 0 AND relationship_score <= 100),
    last_discussion TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- One memory per contact
    CONSTRAINT unique_contact_memory UNIQUE (contact_id)
);

-- Indexes
CREATE INDEX idx_contact_memories_contact_id ON contact_memories(contact_id);
CREATE INDEX idx_contact_memories_score ON contact_memories(relationship_score);
-- GIN index for JSON fields
CREATE INDEX idx_contact_memories_skills ON contact_memories USING GIN(skills);
CREATE INDEX idx_contact_memories_interests ON contact_memories USING GIN(interests);
```

### 3.6 Recommendation

```sql
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('FOLLOWUP', 'REPLY', 'TAG', 'MERGE', 'CONNECTION', 'PRIORITY')),
    reason TEXT,
    priority VARCHAR(10) DEFAULT 'MEDIUM' CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW')),
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'ACCEPTED', 'REJECTED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_recommendations_contact_id ON recommendations(contact_id);
CREATE INDEX idx_recommendations_type ON recommendations(type);
CREATE INDEX idx_recommendations_status ON recommendations(status);
CREATE INDEX idx_recommendations_priority ON recommendations(priority);
CREATE INDEX idx_recommendations_created_at ON recommendations(created_at DESC);
-- For fetching pending recommendations
CREATE INDEX idx_recommendations_pending ON recommendations(status, created_at DESC);
```

### 3.7 Tag

```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    color VARCHAR(20) DEFAULT '#6E6E73',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_tag_name UNIQUE (name)
);

-- Indexes
CREATE INDEX idx_tags_name ON tags(name);
```

### 3.8 ContactTag (Many-to-Many)

```sql
CREATE TABLE contact_tags (
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (contact_id, tag_id)
);

-- Indexes
CREATE INDEX idx_contact_tags_tag_id ON contact_tags(tag_id);
```

### 3.9 EventLog

```sql
CREATE TABLE event_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,
    payload JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_event_logs_user_id ON event_logs(user_id);
CREATE INDEX idx_event_logs_conversation_id ON event_logs(conversation_id);
CREATE INDEX idx_event_logs_type ON event_logs(event_type);
CREATE INDEX idx_event_logs_created_at ON event_logs(created_at DESC);
-- For worker to fetch unprocessed events
CREATE INDEX idx_event_logs_created_unprocessed ON event_logs(created_at) WHERE processed = FALSE;
```

### 3.10 SearchHistory

```sql
CREATE TABLE search_histories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    result_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_search_histories_user_id ON search_histories(user_id);
CREATE INDEX idx_search_histories_created_at ON search_histories(created_at DESC);
```

### 3.11 Notification

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('RECOMMENDATION', 'FOLLOWUP', 'MEMORY_UPDATED')),
    title VARCHAR(255) NOT NULL,
    content TEXT,
    status VARCHAR(20) DEFAULT 'UNREAD' CHECK (status IN ('UNREAD', 'READ')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
```

### 3.12 Setting

```sql
CREATE TABLE settings (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    auto_tag BOOLEAN DEFAULT FALSE,
    auto_memory BOOLEAN DEFAULT TRUE,
    theme VARCHAR(20) DEFAULT 'light' CHECK (theme IN ('light', 'dark', 'system')),
    language VARCHAR(10) DEFAULT 'vi',
    notification BOOLEAN DEFAULT TRUE
);
```

---

## 4. Vector Database Schema (ChromaDB)

### 4.1 Collection: contact_memory_embeddings

```python
collection_name = "contact_memory_embeddings"

# Schema
{
    "id": "uuid-string",
    "contact_id": "uuid-string",
    "summary": "Text summary of contact",
    "embedding": [0.1, 0.2, ...],  # 1536 dimensions (text-embedding-3-small)
    "metadata": {
        "user_id": "uuid-string",
        "company": "VinAI",
        "profession": "AI Engineer",
        "skills": ["AI", "Python"],
        "interests": ["Startup", "Technology"],
        "relationship_score": 75,
        "updated_at": "2026-08-13T10:00:00Z"
    }
}

# Index Configuration
index_type = "hnsw"
metric = "cosine"
```

### 4.2 Collection: message_embeddings

```python
collection_name = "message_embeddings"

# Schema
{
    "id": "uuid-string",
    "conversation_id": "uuid-string",
    "chunk": "A segment of conversation text",
    "embedding": [0.1, 0.2, ...],
    "metadata": {
        "user_id": "uuid-string",
        "contact_id": "uuid-string",
        "sender_type": "USER | CONTACT",
        "created_at": "2026-08-13T10:00:00Z"
    }
}
```

### 4.3 Collection: recommendation_embeddings (Future)

```python
collection_name = "recommendation_embeddings"

# Schema
{
    "id": "uuid-string",
    "recommendation_id": "uuid-string",
    "reason": "Why this recommendation was made",
    "embedding": [0.1, 0.2, ...],
    "metadata": {
        "user_id": "uuid-string",
        "contact_id": "uuid-string",
        "type": "FOLLOWUP | REPLY | ...",
        "created_at": "2026-08-13T10:00:00Z"
    }
}
```

---

## 5. Graph Database Schema (Neo4j - Future)

### 5.1 Node Types

```cypher
// User Node
(:User {
    id: UUID,
    email: String,
    full_name: String,
    created_at: DateTime
})

// Contact Node
(:Contact {
    id: UUID,
    display_name: String,
    avatar: String,
    relationship_score: Integer,
    created_at: DateTime
})

// Company Node
(:Company {
    id: UUID,
    name: String,
    industry: String
})

// Skill Node
(:Skill {
    id: UUID,
    name: String,
    category: String
})

// Topic Node
(:Topic {
    id: UUID,
    name: String
})

// Interest Node
(:Interest {
    id: UUID,
    name: String
})

// Location Node
(:Location {
    id: UUID,
    city: String,
    country: String
})
```

### 5.2 Relationship Types

```cypher
// User knows Contact
(u:User)-[:KNOWS {
    since: DateTime,
    context: String,
    score: Integer
}]->(c:Contact)

// Contact works at Company
(c:Contact)-[:WORKS_AT {
    position: String,
    since: DateTime
}]->(co:Company)

// Contact interested in Topic
(c:Contact)-[:INTERESTED_IN {
    score: Integer,
    last_mentioned: DateTime
}]->(t:Topic)

// Contact has Skill
(c:Contact)-[:HAS_SKILL {
    level: String,
    years_experience: Integer
}]->(s:Skill)

// Contact located in Location
(c:Contact)-[:LOCATED_IN]->(l:Location)

// Contact talked about Topic
(c:Contact)-[:TALKED_ABOUT {
    frequency: Integer,
    last_mentioned: DateTime
}]->(t:Topic)

// Contact connected to another Contact
(c1:Contact)-[:CONNECTED_TO {
    reason: String,
    strength: Integer
}]->(c2:Contact)
```

---

## 6. Indexing Strategy

### 6.1 SQLite Indexes (MVP)

```sql
-- Single column indexes
CREATE INDEX idx_contacts_user_id ON contacts(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_event_logs_user_id ON event_logs(user_id);

-- Composite indexes
CREATE INDEX idx_conversations_user_contact ON conversations(user_id, contact_id);
CREATE INDEX idx_messages_conv_time ON messages(conversation_id, created_at DESC);
```

### 6.2 PostgreSQL Indexes (Future)

```sql
-- Partial indexes for common queries
CREATE INDEX idx_messages_recent ON messages(conversation_id, created_at DESC)
WHERE created_at > NOW() - INTERVAL '30 days';

-- Expression indexes
CREATE INDEX idx_contacts_name_lower ON contacts(LOWER(display_name));

-- Covering indexes
CREATE INDEX idx_messages_covering ON messages(conversation_id, created_at DESC)
INCLUDE (sender_type, content);
```

### 6.3 ChromaDB/Qdrant Index

```python
# HNSW Index Configuration
{
    "hnsw:space": "cosine",
    "hnsw:ef_construction": 128,
    "hnsw:M": 16,
    "hnsw:ef_search": 128
}
```

---

## 7. Data Access Patterns

### 7.1 Read Patterns

| Pattern | Database | Query |
|---------|----------|-------|
| Get user's conversations | SQLite | `SELECT * FROM conversations WHERE user_id = ? ORDER BY last_message_time DESC` |
| Get messages for chat | SQLite | `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC LIMIT 50` |
| Get contact memory | SQLite | `SELECT * FROM contact_memories WHERE contact_id = ?` |
| Semantic search contacts | ChromaDB | `collection.query(query_embedding, n_results=10)` |
| Get recommendations | SQLite | `SELECT * FROM recommendations WHERE contact_id = ? AND status = 'PENDING'` |
| Get knowledge graph | Neo4j | `MATCH (c:Contact {id: ?})-[:INTERESTED_IN]->(t:Topic) RETURN t` |

### 7.2 Write Patterns

| Pattern | Database | Operation |
|---------|----------|-----------|
| Save message | SQLite | `INSERT INTO messages (conversation_id, sender_type, content) VALUES (?, ?, ?)` |
| Update memory | SQLite | `UPDATE contact_memories SET summary = ?, updated_at = NOW()` |
| Save embedding | ChromaDB | `collection.upsert(ids, embeddings, metadatas)` |
| Log event | SQLite | `INSERT INTO event_logs (user_id, event_type, payload) VALUES (?, ?, ?)` |
| Create relationship | Neo4j | `MATCH (c:Contact), (co:Company) CREATE (c)-[:WORKS_AT]->(co)` |

---

## 8. Data Isolation

### 8.1 User Data Isolation

Every data access MUST filter by `user_id`:

```python
# ✅ Correct - Always filter by user_id
messages = db.query(Message).filter(
    Message.conversation_id == conversation_id,
    Conversation.user_id == current_user.id  # Critical!
).all()

# ❌ Wrong - Missing user_id filter
messages = db.query(Message).filter(
    Message.conversation_id == conversation_id
).all()
```

### 8.2 Row-Level Security (Future)

```sql
-- Enable RLS in PostgreSQL
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;

-- Policy to ensure users only see their own contacts
CREATE POLICY user_contacts ON contacts
    FOR ALL
    USING (user_id = current_user_id());
```

---

## 9. Data Retention

### 9.1 Retention Policy

| Data Type | MVP Retention | Post-MVP |
|-----------|---------------|----------|
| Messages | Forever | Forever (user can delete) |
| Contact Memory | Forever | Forever |
| Search History | 90 days | Configurable |
| Event Logs | 30 days | 90 days |
| Notifications | 30 days | 90 days |
| Embeddings | Sync with Memory | Sync with Memory |

### 9.2 Cleanup Jobs

```python
# Scheduled cleanup (Post-MVP)
async def cleanup_old_data():
    # Delete old search history
    await db.execute("""
        DELETE FROM search_histories 
        WHERE created_at < NOW() - INTERVAL '90 days'
    """)
    
    # Delete old event logs
    await db.execute("""
        DELETE FROM event_logs 
        WHERE created_at < NOW() - INTERVAL '30 days'
        AND processed = TRUE
    """)
```

---

## 10. Backup & Recovery

### 10.1 Backup Strategy

| Database | MVP Backup | Post-MVP Backup |
|----------|------------|-----------------|
| SQLite | File copy | — |
| PostgreSQL | — | pg_dump daily + WAL archiving |
| ChromaDB | File copy | Snapshot + replication |
| Neo4j | — | Neo4j backup |
| Redis | — | RDB snapshots |

### 10.2 Recovery Plan

1. **Full Database Failure**
   - Restore from latest backup
   - Replay WAL (PostgreSQL)
   - Verify data integrity

2. **Single Table Corruption**
   - Restore table from backup
   - Use point-in-time recovery if available

3. **Accidental Deletion**
   - Soft delete implementation for critical data
   - Audit log for tracking changes

---

## 11. Database Migrations

### 11.1 Migration Tool: Alembic

```bash
# Create migration
alembic revision --autogenerate -m "Add contact memories table"

# Run migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### 11.2 Migration Example

```python
# alembic/versions/001_add_contact_memories.py

def upgrade():
    op.create_table(
        'contact_memories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('contact_id', sa.UUID(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('profession', sa.String(length=255), nullable=True),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('skills', JSON, nullable=True),
        sa.Column('interests', JSON, nullable=True),
        sa.Column('relationship_score', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contact_id')
    )

def downgrade():
    op.drop_table('contact_memories')
```

---

*Document Version: 1.0*  
*Last Updated: 2026-08-13*
