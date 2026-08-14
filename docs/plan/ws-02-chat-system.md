# WS-02 — Chat System

> **Mục tiêu:** Hoàn thiện Chat (REST + WebSocket), Contact Management, Friends System, Event Bus.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | WS-02 (sau WS-01) |
| Độ phức tạp | 🟡 Trung bình |
| Phụ thuộc | WS-01 (Backend Foundation) |
| Unblock | WS-03, WS-04, WS-05, WS-06 |

---

## Trạng thái hiện tại

| Component | Status | File |
|-----------|--------|------|
| Pydantic Schemas | ✅ Done | `src/schemas/` |
| Contact API | ✅ Done | `src/api/v1/contacts.py` |
| Conversation API | ✅ Done | `src/api/v1/conversations.py` |
| Message API | ✅ Done | `src/api/v1/messages.py` |
| Friends API | ✅ Done | `src/api/v1/friends.py` |
| WebSocket Manager | ✅ Done | `src/ws/manager.py` |
| WebSocket Endpoint | ✅ Done | `src/api/ws.py` |
| Event Bus | ✅ Done | `src/events/bus.py` |

---

## Multi-User Chat Architecture

### Real-time Message Flow

```
User A sends message
        │
        ▼
┌─────────────────┐
│  POST /messages │
└────────┬────────┘
         │
         ├──────────────────────────────────────┐
         │                                      │
         ▼                                      ▼
┌─────────────────┐              ┌─────────────────┐
│  Save to DB     │              │  Find ConversationPair │
└────────┬────────┘              └────────┬────────┘
         │                                      │
         │                                      ▼
         │              ┌─────────────────────────────┐
         │              │  Get other user's conversation │
         │              └─────────────┬───────────────┘
         │                                │
         │                                ▼
         │              ┌─────────────────────────────┐
         │              │  Save to OTHER user's DB    │
         │              │  (via ConversationPair)      │
         │              └─────────────┬───────────────┘
         │                                │
         │                                ▼
         │              ┌─────────────────────────────┐
         │              │  WebSocket broadcast to      │
         │              │  OTHER user                 │
         │              └─────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  WebSocket      │
│  broadcast to    │
│  User A (self)  │
└─────────────────┘
```

### ConversationPair Design

```python
# When User A and User B become friends:
# 1. Create ConversationPair
# 2. Create Conversation for User A (belongs to User A's contacts)
# 3. Create Conversation for User B (belongs to User B's contacts)
# 4. Both conversations reference the same conversation_pair_id

ConversationPair:
  id = uuid
  user_1_id = A
  user_2_id = B

Conversation (for A):
  id = uuid_A
  user_id = A
  contact_id = A's_contact_for_B
  conversation_pair_id = pair.id

Conversation (for B):
  id = uuid_B
  user_id = B
  contact_id = B's_contact_for_A
  conversation_pair_id = pair.id

# Message sent from A:
# 1. Save to conversation uuid_A with sender_id = A
# 2. WebSocket notify A (self)
# 3. Lookup conversation with same conversation_pair_id for B
# 4. Save to conversation uuid_B with sender_id = A
# 5. WebSocket notify B (real-time)
```

---

## TASK-CHAT-01: Pydantic Schemas ✅

**Mô tả:** Định nghĩa request/response schemas.

**Files Created:**

- `src/schemas/auth.py` — Auth schemas
- `src/schemas/contact.py` — Contact schemas
- `src/schemas/conversation.py` — Conversation schemas
- `src/schemas/message.py` — Message schemas
- `src/schemas/friend.py` — Friend request schemas
- `src/schemas/memory.py` — Memory schemas
- `src/schemas/recommendation.py` — Recommendation schemas
- `src/schemas/search.py` — Search schemas
- `src/schemas/copilot.py` — Copilot schemas
- `src/schemas/common.py` — Common schemas (pagination, response wrapper)

**Schemas:**

```python
# Contact
ContactBase, ContactCreate, ContactUpdate, ContactResponse
FriendRequestCreate, FriendRequestResponse
FriendResponse

# Conversation
ConversationBase, ConversationCreate, ConversationResponse
ConversationWithMessages

# Message
MessageBase, MessageCreate, MessageResponse
MessageListResponse
```

---

## TASK-CHAT-02: Contact API ✅

**Mô tả:** REST API cho Contact + Friends System.

**Endpoints:**

```
# Contact CRUD
GET    /api/v1/contacts              — List contacts
POST   /api/v1/contacts              — Create contact
GET    /api/v1/contacts/{id}        — Get contact
PATCH  /api/v1/contacts/{id}        — Update contact
DELETE /api/v1/contacts/{id}        — Delete contact

# Friends System (search by phone, request/accept)
GET    /api/v1/friends/search        — Search by phone number
POST   /api/v1/friends/request       — Send friend request
GET    /api/v1/friends/requests     — List incoming requests
POST   /api/v1/friends/request/{id}/accept  — Accept request
POST   /api/v1/friends/request/{id}/reject  — Reject request
GET    /api/v1/friends              — List friends
```

---

## TASK-CHAT-03: Conversation API ✅

**Mô tả:** REST API cho Conversation.

**Endpoints:**

```
GET    /api/v1/conversations              — List conversations
POST   /api/v1/conversations              — Create conversation
GET    /api/v1/conversations/{id}         — Get conversation
PATCH  /api/v1/conversations/{id}         — Update (title, status)
DELETE /api/v1/conversations/{id}        — Delete conversation
```

---

## TASK-CHAT-04: Message API ✅

**Mô tả:** REST API cho Message.

**Endpoints:**

```
GET    /api/v1/conversations/{id}/messages  — List messages
POST   /api/v1/conversations/{id}/messages  — Send message
PATCH  /api/v1/messages/{id}/read           — Mark as read
DELETE /api/v1/messages/{id}               — Delete message
```

**Flow:**

1. Save message to sender's conversation
2. Lookup ConversationPair
3. Save to receiver's conversation (via ConversationPair)
4. Emit SEND_MESSAGE event
5. Broadcast via WebSocket to both users

---

## TASK-CHAT-05: WebSocket + Connection Manager ✅

**Mô tả:** WebSocket endpoint cho realtime chat.

**WebSocket Endpoint:**

```
WS /ws/{token}        — Real-time chat (auth via token)
```

**Features:**

- JWT authentication via query param or header
- Connection per conversation
- Broadcast to all users in conversation
- Auto-reconnect support
- Heartbeat ping/pong

**Manager Features:**

```python
class ConnectionManager:
    # Track connections per conversation
    active_connections: dict[str, list[WebSocket]]
    
    async def connect(ws: WebSocket, conversation_id: str, user_id: str)
    async def disconnect(ws: WebSocket, conversation_id: str, user_id: str)
    async def broadcast(conversation_id: str, message: dict)
    async def send_personal(user_id: str, message: dict)
```

---

## TASK-CHAT-06: Event Bus ✅

**Mô tả:** Event Bus cho async processing.

**Event Types:**

```python
class EventType(str, Enum):
    # Chat Events
    SEND_MESSAGE = "SEND_MESSAGE"
    RECEIVE_MESSAGE = "RECEIVE_MESSAGE"
    READ_MESSAGE = "READ_MESSAGE"
    OPEN_CHAT = "OPEN_CHAT"
    CLOSE_CHAT = "CLOSE_CHAT"
    
    # Friend Events
    FRIEND_REQUEST_SENT = "FRIEND_REQUEST_SENT"
    FRIEND_REQUEST_RECEIVED = "FRIEND_REQUEST_RECEIVED"
    FRIEND_REQUEST_ACCEPTED = "FRIEND_REQUEST_ACCEPTED"
    FRIEND_REQUEST_REJECTED = "FRIEND_REQUEST_REJECTED"
    
    # AI Events
    OPEN_AI = "OPEN_AI"
    MEMORY_UPDATED = "MEMORY_UPDATED"
    RECOMMENDATION_CREATED = "RECOMMENDATION_CREATED"
```

**Bus Features:**

- Asyncio-based dispatcher
- Event persistence to EventLog table
- Subscribe/unsubscribe pattern
- Graceful error handling
- Background dispatch loop

---

## Friends System Flow

```
User A searches by phone number
        │
        ▼
┌─────────────────┐
│ GET /friends/   │
│ search?phone=  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Find User B     │
│ by phone        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ POST /friends/  │
│ request         │
└────────┬────────┘
         │
         ├──────────────────────────────────────┐
         │                                      │
         ▼                                      ▼
┌─────────────────┐              ┌─────────────────┐
│ Create          │              │ Notify User B   │
│ FriendRequest   │              │ (notification)  │
└─────────────────┘              └─────────────────┘

User B views requests
        │
        ▼
┌─────────────────┐
│ GET /friends/   │
│ requests        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ POST /friends/ │
│ request/accept │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ 1. Create ConversationPair                  │
│ 2. Create Contact for A in B's contact list │
│ 3. Create Contact for B in A's contact list│
│ 4. Create Conversation for A               │
│ 5. Create Conversation for B               │
│ 6. Both reference same conversation_pair_id│
│ 7. Notify both users                      │
└─────────────────────────────────────────────┘
```

---

## Kết quả mong đợi sau WS-02

```
✅ APIs Contact/Conversation/Message hoạt động qua Swagger
✅ Friends System (search by phone, request/accept/reject)
✅ WebSocket gửi/nhận realtime giữa 2 users
✅ ConversationPair syncs messages giữa 2 users
✅ EventBus ghi nhận event và dispatch được
✅ Test API + WebSocket pass
```

---

## Trạng thái hoàn thành

| Task | Status | Evidence |
|------|--------|----------|
| TASK-CHAT-01: Pydantic Schemas | ✅ Done | `src/schemas/` |
| TASK-CHAT-02: Contact API | ✅ Done | `src/api/v1/contacts.py`, `friends.py` |
| TASK-CHAT-03: Conversation API | ✅ Done | `src/api/v1/conversations.py` |
| TASK-CHAT-04: Message API | ✅ Done | `src/api/v1/messages.py` |
| TASK-CHAT-05: WebSocket | ✅ Done | `src/api/ws.py`, `src/ws/manager.py` |
| TASK-CHAT-06: Event Bus | ✅ Done | `src/events/bus.py` |

---

## Reference

- [API Documentation](../specs/api.md)
- [Architecture - Data Flow](../specs/architecture.md#3-data-flow-architecture)
- [Database Schema](../specs/database.md)

---

*Version: 2.0 (Specv2 aligned)*
*Last Updated: 2026-08-14*
