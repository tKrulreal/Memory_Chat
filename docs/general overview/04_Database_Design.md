# 04_Database_Design.md

# Database Design

Project: MemoryChat

Version: MVP v1.0

---

# 1. Overview

MemoryChat hướng tới mô hình **Polyglot Persistence** — mỗi loại dữ liệu được lưu ở database phù hợp nhất với đặc tính và cách truy vấn của nó.

Tuy nhiên, để phù hợp với thời gian MVP (6 tuần) và giảm chi phí vận hành, giai đoạn đầu sử dụng cấu hình đơn giản. Các thành phần sẽ được tách ra khi scale.

| Database        | Vai trò                  | Giai đoạn MVP   |
|-----------------|--------------------------|-----------------|
| SQLite          | Transactional Data       | ✅ Đang dùng    |
| ChromaDB        | Embedding / Semantic Search | ✅ Đang dùng |
| PostgreSQL      | Transactional Data       | ⬜ Sau MVP      |
| Qdrant          | Semantic Search          | ⬜ Sau MVP      |
| Neo4j           | Relationship Graph       | ⬜ Sau MVP      |
| Redis           | Cache, Session, Event Bus| ⬜ Sau MVP      |

Trong MVP:
- **SQLite** là Source of Truth.
- **ChromaDB** lưu vector embedding của Contact Memory và Message.
- LLM cache tạm thời trong memory + file cache (`.ai-log/`).

Sau MVP sẽ tách thành **Polyglot Persistence** đầy đủ.

---

# 2. Source of Truth (SQLite — giai đoạn MVP)

Trong MVP, toàn bộ dữ liệu nghiệp vụ được lưu trong SQLite.

File mặc định: `./data/app.db` (xem `DATABASE_URL` trong `.env.example`).

Lý do chọn SQLite cho MVP:

- Không cần cài thêm service.
- Phù hợp với development + demo.
- Dễ dàng migrate sang PostgreSQL sau này thông qua ORM.

Các bảng nghiệp vụ chính:

- User
- Contact
- Conversation
- Message
- ContactMemory
- Recommendation
- EventLog
- SearchHistory
- Notification
- Setting
- Tag
- ContactTag

---

# 3. Database Schema (chuẩn hoá theo MVP)

Schema dưới đây là **chuẩn hoá cuối cùng** — áp dụng được cho cả SQLite (MVP) lẫn PostgreSQL (sau MVP). Sử dụng ORM để chuyển đổi không cần sửa logic.

## User

```
User
  id                — UUID
  email             — unique
  password_hash
  full_name
  avatar
  created_at
  updated_at
```

Mỗi User sở hữu nhiều Contact và Conversation.

---

## Contact

```
Contact
  id                — UUID
  user_id           — FK User
  display_name
  avatar
  phone
  email
  created_at
  updated_at
```

Một Contact chỉ thuộc về một User.

Điều này đảm bảo dữ liệu riêng tư giữa các người dùng — ContactMemory cho cùng một người nhưng khác User sẽ hoàn toàn khác nhau.

---

## Conversation

```
Conversation
  id                — UUID
  user_id           — FK User
  contact_id        — FK Contact
  last_message
  last_message_time
  created_at
  updated_at
```

Một Conversation tương ứng với một Contact trong MVP.

(Group Chat sẽ được mở rộng sau.)

---

## Message

```
Message
  id                — UUID
  conversation_id   — FK Conversation
  sender_type       — USER | CONTACT
  content
  message_type      — TEXT | AI | SYSTEM
  created_at
```

Message chỉ lưu dữ liệu gốc.

Không lưu Summary. Không lưu Memory tại đây.

---

## ContactMemory

Đây là bảng quan trọng nhất — lưu tri thức do AI sinh ra.

```
ContactMemory
  id                 — UUID
  contact_id         — FK Contact
  summary            — text
  profession
  company
  skills             — JSON
  interest           — JSON
  timeline           — JSON
  relationship_score — 0–100
  last_discussion
  updated_at
```

ContactMemory được tạo hoàn toàn bởi AI.

Người dùng có thể chỉnh sửa nếu cần.

---

## Recommendation

```
Recommendation
  id          — UUID
  contact_id  — FK Contact
  type        — FOLLOWUP | REPLY | TAG | MERGE | CONNECTION | PRIORITY
  reason
  priority    — HIGH | MEDIUM | LOW
  status      — PENDING | ACCEPTED | REJECTED
  created_at
```

Recommendation KHÔNG được AI tự động thực hiện.

---

## Tag

```
Tag
  id
  name
  color
  created_at
```

---

## ContactTag

```
ContactTag
  contact_id  — FK Contact
  tag_id      — FK Tag
```

Quan hệ nhiều-nhiều.

---

## SearchHistory

```
SearchHistory
  id
  user_id     — FK User
  query
  result_count
  created_at
```

Dùng để phân tích hành vi và cải thiện Recommendation.

---

## Notification

```
Notification
  id
  user_id     — FK User
  type        — RECOMMENDATION | FOLLOWUP | MEMORY_UPDATED
  title
  content
  status      — UNREAD | READ
  created_at
```

---

## Setting

```
Setting
  user_id     — PK/FK User
  auto_tag        — bool
  auto_memory     — bool
  theme
  language
  notification    — bool
```

---

## EventLog

Bảng quan trọng phục vụ event-driven AI.

```
EventLog
  id
  user_id          — FK User
  conversation_id  — FK Conversation (nullable)
  event_type
  payload          — JSON
  created_at
```

Các event_type:

```
OPEN_CHAT
SEND_MESSAGE
SEARCH
PIN_CONTACT
APPROVE_TAG
REJECT_TAG
OPEN_AI
SHARE_TO_CONVERSATION
CONTACT_UPDATED
```

---

# 4. ER Diagram (chuẩn hoá)

```
User
 │
 ├── Contact
 │      ├── ContactMemory
 │      └── ContactTag ── Tag
 │
 ├── Conversation
 │      └── Message
 │
 ├── SearchHistory
 ├── Notification
 └── Setting

Recommendation ──▶ Contact
```

---

# 5. Vector Database (ChromaDB — MVP)

ChromaDB chịu trách trách nhiệm Semantic Search.

Không lưu dữ liệu gốc — chỉ lưu embedding + metadata.

Collection mặc định:

## contact_memory_embedding

```
id
contact_id
summary
embedding
metadata { user_id, company, ... }
```

## message_embedding

```
id
conversation_id
chunk
embedding
metadata { user_id, contact_id, ... }
```

## recommendation_embedding

Mở rộng sau.

---

# 6. Polyglot Persistence (kế hoạch sau MVP)

Sau MVP, hệ thống sẽ tách thành các database chuyên dụng:

| Database    | Vai trò                              | Thay thế      |
|-------------|--------------------------------------|---------------|
| PostgreSQL  | Transactional Data                   | SQLite        |
| Qdrant      | Vector Search                        | ChromaDB      |
| Neo4j       | Relationship Graph                   | Bổ sung mới   |
| Redis       | Cache, Session, Event Bus            | Bổ sung mới   |

### Knowledge Graph (Neo4j)

Node:

- User
- Contact
- Company
- Skill
- Topic
- Interest
- Organization
- Location

Edge (ví dụ):

- `(User)-[:KNOW]->(Contact)`
- `(Contact)-[:WORK_AT]->(Company)`
- `(Contact)-[:INTEREST_IN]->(Topic)`
- `(Contact)-[:HAS_SKILL]->(Skill)`
- `(Contact)-[:LOCATED_IN]->(Location)`

AI Recommendation sẽ truy vấn Neo4j thay vì PostgreSQL.

---

# 7. Cache Layer (kế hoạch sau MVP)

Redis không lưu dữ liệu lâu dài — chỉ dùng để tăng tốc:

- Recent Conversation
- Conversation Context
- LLM Cache
- JWT Blacklist
- Session
- Recommendation Cache

Trong MVP, các tác vụ này được xử lý tạm thời trong memory của process FastAPI.

---

# 8. Memory Storage Strategy

Memory không được cập nhật sau mỗi tin nhắn.

Workflow tổng quát:

```
Message
  ↓
SQLite (PostgreSQL sau này)
  ↓
Event Queue (in-memory trong MVP)
  ↓
Memory Worker
  ↓
LLM Summary
  ↓
Update ContactMemory
  ↓
Embedding
  ↓
ChromaDB (Qdrant sau này)
  ↓
Recommendation
```

Memory được cập nhật khi:

- Conversation Idle (> 5 phút)
- Conversation Closed
- Đủ 20 tin nhắn mới
- User yêu cầu "Refresh Memory"
- Batch Job ban đêm

---

# 9. Recommendation Storage

Recommendation không được sinh realtime mỗi lần mở ứng dụng.

Recommendation được tạo khi:

- Memory Update
- Event quan trọng
- Batch Job

Điều này giúp giảm số lần gọi LLM.

---

# 10. Indexing Strategy

### SQLite (MVP) — chuyển sang PostgreSQL sau

Index:

```
conversation_id
contact_id
user_id
created_at
```

Composite:

```
(user_id, contact_id)
(conversation_id, created_at)
```

### ChromaDB

- Sử dụng HNSW Index.
- Cosine Similarity.

### Neo4j (kế hoạch)

Index trên: `Company`, `Skill`, `Interest`, `Topic`.

---

# 11. Data Ownership

Mỗi User sở hữu hoàn toàn dữ liệu của mình.

Hai User có thể cùng lưu một Contact, nhưng ContactMemory sẽ hoàn toàn khác nhau.

Ví dụ:

```
User A → Contact "Anh Nam" → Quan tâm AI, gặp ở VinUni
User B → Contact "Anh Nam" → Khách hàng, quan tâm ERP
```

Điều này đảm bảo quyền riêng tư và cá nhân hoá AI.

---

# 12. Database Design Principles

- SQLite (MVP) là Source of Truth, sẽ chuyển sang PostgreSQL khi scale.
- Message là dữ liệu bất biến, không bị AI chỉnh sửa.
- ContactMemory là tri thức do AI tạo ra.
- ChromaDB (sau này Qdrant) chỉ lưu embedding.
- Không gọi LLM sau mỗi tin nhắn.
- Human-in-the-loop cho mọi thay đổi quan trọng.
- Toàn bộ cập nhật AI đều thông qua Event-driven Architecture.