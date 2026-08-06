# WS-02 — Chat System

> **Mục tiêu:** Hoàn thiện Chat (REST + WebSocket), Contact Management, Event Bus in-process.

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

- ✅ `src/api/chat.py` skeleton (gọi LangGraph `analyze` + `respond`).
- ✅ `src/agents/graph.py` skeleton (LangGraph demo).
- ✅ Contact / Conversation / Message API đã có.
- ✅ WebSocket endpoint đã có.
- ✅ Event Bus đã có.

---

## TASK-CHAT-01: Pydantic Schemas (Contact/Conversation/Message) ✅

**Mô tả:** Định nghĩa request/response schemas cho Contact, Conversation, Message.

**Checklist:**
- [x] Tạo `src/schemas/__init__.py`
- [x] `ContactBase`, `ContactCreate`, `ContactUpdate`, `ContactResponse`
- [x] `ConversationBase`, `ConversationCreate`, `ConversationResponse`
- [x] `MessageBase`, `MessageCreate`, `MessageResponse`
- [x] `MessageRole` enum (`USER`, `CONTACT`, `AI`)
- [x] `ConversationStatus` enum (`OPEN`, `CLOSED`, `ARCHIVED`)
- [x] Validation: `name` không rỗng, `content` không rỗng
- [x] Config ORM mode cho Pydantic v2

**Commands:**
```bash
mkdir -p src/schemas
pytest tests/unit/schemas -v
```

---

## TASK-CHAT-02: Contact API (CRUD) ✅

**Mô tả:** REST API cho Contact — tạo, liệt kê, sửa, xoá.

**Endpoints:**

```
GET    /api/v1/contacts          — Liệt kê Contact của user
POST   /api/v1/contacts          — Tạo Contact mới
GET    /api/v1/contacts/{id}     — Chi tiết Contact
PUT    /api/v1/contacts/{id}     — Cập nhật Contact
DELETE /api/v1/contacts/{id}     — Xoá Contact
```

**Checklist:**
- [x] Tạo `src/api/contacts.py` router
- [x] Inject `ContactService` qua Depends
- [x] Apply `get_current_user` (auth)
- [x] Pagination: `?page=1&limit=20`
- [x] Filter: `?search=keyword`
- [x] Response shape chuẩn: `{ data, pagination }`
- [x] Error handling: 404 nếu không tìm thấy, 403 nếu không phải owner

**Commands:**
```bash
# Test API
curl -X POST http://localhost:8000/api/v1/contacts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Nguyễn Văn A","avatar_url":"https://..."}'

curl http://localhost:8000/api/v1/contacts \
  -H "Authorization: Bearer $TOKEN"
```

---

## TASK-CHAT-03: Conversation API (CRUD) ✅

**Mô tả:** REST API cho Conversation — tạo, liệt kê, lấy chi tiết.

**Endpoints:**

```
GET    /api/v1/conversations              — Liệt kê Conversation của user
POST   /api/v1/conversations              — Tạo Conversation mới với Contact
GET    /api/v1/conversations/{id}         — Chi tiết Conversation
PATCH  /api/v1/conversations/{id}         — Cập nhật (title, status)
DELETE /api/v1/conversations/{id}         — Xoá Conversation
```

**Checklist:**
- [x] Tạo `src/api/conversations.py` router
- [x] Inject `ConversationService` qua Depends
- [x] Apply `get_current_user` (auth)
- [x] Sinh Event `OPEN_CHAT` khi tạo conversation
- [x] Sinh Event `CLOSE_CHAT` khi status → CLOSED
- [x] Filter: `?status=OPEN&contact_id=...`
- [x] Sort: `last_message_at DESC`
- [x] Include `last_message` preview trong list response

**Commands:**
```bash
# Test API
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contact_id":1,"title":"Chat với A"}'
```

---

## TASK-CHAT-04: Message API (CRUD) ✅ (Memory Worker deferred to WS-03)

**Mô tả:** REST API cho Message — gửi, liệt kê, lấy chi tiết.

**Endpoints:**

```
GET  /api/v1/conversations/{id}/messages           — Liệt kê Message trong conversation
POST /api/v1/conversations/{id}/messages           — Gửi Message mới
GET  /api/v1/messages/{id}                          — Chi tiết Message
DELETE /api/v1/messages/{id}                        — Xoá Message
```

**Checklist:**
- [x] Tạo `src/api/messages.py` router
- [x] Inject `MessageService` qua Depends
- [x] Sinh Event `SEND_MESSAGE` mỗi khi có message mới
- [x] Update `Conversation.last_message_at` mỗi khi gửi
- [x] Pagination: `?page=1&limit=50`
- [ ] Trigger Memory Worker qua EventBus (chuẩn bị cho WS-03)
- [x] Response bao gồm `id`, `role`, `content`, `created_at`

**Commands:**
```bash
# Test gửi message
curl -X POST http://localhost:8000/api/v1/conversations/1/messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Xin chào!","role":"USER"}'
```

---

## TASK-CHAT-05: WebSocket + Connection Manager ✅

**Mô tả:** WebSocket endpoint cho realtime chat + Connection Manager (in-memory dict).

**WebSocket endpoint:**

```
WS /ws/chat/{conversation_id}        — Realtime chat (gửi/nhận Message)
```

**Checklist:**
- [x] Tạo `src/api/ws.py` (WebSocket endpoint)
- [x] Tạo `src/ws/manager.py` (ConnectionManager class)
- [x] Method `connect(websocket, conversation_id)` — accept + lưu vào dict
- [x] Method `disconnect(websocket, conversation_id)` — remove khỏi dict
- [x] Method `broadcast(conversation_id, message)` — gửi cho tất cả client cùng conversation
- [x] Khi nhận message qua WS → lưu DB + broadcast
- [x] Khi nhận message qua WS → emit Event `SEND_MESSAGE` qua EventBus
- [x] Heartbeat ping/pong mỗi 30s
- [x] Auto-reconnect support (client side)
- [x] Test với 2 client giả lập (WebSocketTest client)

**Commands:**
```bash
# Test WebSocket với wscat
wscat -c ws://localhost:8000/ws/chat/1 \
  -H "Authorization: Bearer $TOKEN"
# Gửi: {"content":"Hello"}
```

---

## TASK-CHAT-06: Event Bus (asyncio + EventLog) ✅

**Mô tả:** Event Bus đơn giản — ghi vào `EventLog` + asyncio dispatcher loop.

**Checklist:**
- [x] Tạo `src/events/bus.py` (EventBus singleton)
- [x] Method `publish(event_type, payload)` — enqueue vào asyncio.Queue
- [x] Method `subscribe(event_type, handler)` — đăng ký handler
- [x] Background task `dispatcher_loop()` chạy trong lifespan
- [x] Mỗi event ghi vào `EventLog` (event_type, payload, created_at)
- [x] Gọi các handler đã subscribe
- [x] Handler fail không crash dispatcher (log + skip)
- [x] Event types: `SEND_MESSAGE`, `OPEN_CHAT`, `CLOSE_CHAT`, `MEMORY_REFRESH`, `OPEN_AI`
- [x] Test E2E: gửi message → EventBus ghi EventLog → handler nhận

**Commands:**
```bash
# Test EventBus
python -c "
import asyncio
from src.events.bus import EventBus

async def main():
    bus = EventBus()
    await bus.publish('SEND_MESSAGE', {'msg': 'hello'})
    await asyncio.sleep(0.5)
    print(await bus.list_recent())

asyncio.run(main())
"
```

---

## Kết quả mong đợi sau WS-02

```
✅ APIs Contact/Conversation/Message hoạt động qua Swagger
✅ WebSocket gửi/nhận realtime giữa 2 client
✅ EventBus ghi nhận event và dispatch được
✅ Sau mỗi message, Event SEND_MESSAGE có trong EventLog
✅ Test API + WebSocket pass
✅ Không ảnh hưởng endpoint /api/v1/chat hiện tại (giữ nguyên LangGraph demo)
```
