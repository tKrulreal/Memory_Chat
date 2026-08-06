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
- ⬜ Contact / Conversation / Message API chưa có.
- ⬜ WebSocket endpoint chưa có.
- ⬜ Event Bus chưa có.

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

## TASK-CHAT-02: Contact API (CRUD) ⬜

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
- [ ] Tạo `src/api/contacts.py` router
- [ ] Inject `ContactService` qua Depends
- [ ] Apply `get_current_user` (auth)
- [ ] Pagination: `?page=1&limit=20`
- [ ] Filter: `?search=keyword`
- [ ] Response shape chuẩn: `{ data, pagination }`
- [ ] Error handling: 404 nếu không tìm thấy, 403 nếu không phải owner

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

## TASK-CHAT-03: Conversation API (CRUD) ⬜

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
- [ ] Tạo `src/api/conversations.py` router
- [ ] Inject `ConversationService` qua Depends
- [ ] Apply `get_current_user` (auth)
- [ ] Sinh Event `OPEN_CHAT` khi tạo conversation
- [ ] Sinh Event `CLOSE_CHAT` khi status → CLOSED
- [ ] Filter: `?status=OPEN&contact_id=...`
- [ ] Sort: `last_message_at DESC`
- [ ] Include `last_message` preview trong list response

**Commands:**
```bash
# Test API
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contact_id":1,"title":"Chat với A"}'
```

---

## TASK-CHAT-04: Message API (CRUD) ⬜

**Mô tả:** REST API cho Message — gửi, liệt kê, lấy chi tiết.

**Endpoints:**

```
GET  /api/v1/conversations/{id}/messages           — Liệt kê Message trong conversation
POST /api/v1/conversations/{id}/messages           — Gửi Message mới
GET  /api/v1/messages/{id}                          — Chi tiết Message
DELETE /api/v1/messages/{id}                        — Xoá Message
```

**Checklist:**
- [ ] Tạo `src/api/messages.py` router
- [ ] Inject `MessageService` qua Depends
- [ ] Sinh Event `SEND_MESSAGE` mỗi khi có message mới
- [ ] Update `Conversation.last_message_at` mỗi khi gửi
- [ ] Pagination: `?page=1&limit=50`
- [ ] Trigger Memory Worker qua EventBus (chuẩn bị cho WS-03)
- [ ] Response bao gồm `id`, `role`, `content`, `created_at`

**Commands:**
```bash
# Test gửi message
curl -X POST http://localhost:8000/api/v1/conversations/1/messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Xin chào!","role":"USER"}'
```

---

## TASK-CHAT-05: WebSocket + Connection Manager ⬜

**Mô tả:** WebSocket endpoint cho realtime chat + Connection Manager (in-memory dict).

**WebSocket endpoint:**

```
WS /ws/chat/{conversation_id}        — Realtime chat (gửi/nhận Message)
```

**Checklist:**
- [ ] Tạo `src/api/ws.py` (WebSocket endpoint)
- [ ] Tạo `src/ws/manager.py` (ConnectionManager class)
- [ ] Method `connect(websocket, conversation_id)` — accept + lưu vào dict
- [ ] Method `disconnect(websocket, conversation_id)` — remove khỏi dict
- [ ] Method `broadcast(conversation_id, message)` — gửi cho tất cả client cùng conversation
- [ ] Khi nhận message qua WS → lưu DB + broadcast
- [ ] Khi nhận message qua WS → emit Event `SEND_MESSAGE` qua EventBus
- [ ] Heartbeat ping/pong mỗi 30s
- [ ] Auto-reconnect support (client side)
- [ ] Test với 2 client giả lập (WebSocketTest client)

**Commands:**
```bash
# Test WebSocket với wscat
wscat -c ws://localhost:8000/ws/chat/1 \
  -H "Authorization: Bearer $TOKEN"
# Gửi: {"content":"Hello"}
```

---

## TASK-CHAT-06: Event Bus (asyncio + EventLog) ⬜

**Mô tả:** Event Bus đơn giản — ghi vào `EventLog` + asyncio dispatcher loop.

**Checklist:**
- [ ] Tạo `src/events/bus.py` (EventBus singleton)
- [ ] Method `publish(event_type, payload)` — enqueue vào asyncio.Queue
- [ ] Method `subscribe(event_type, handler)` — đăng ký handler
- [ ] Background task `dispatcher_loop()` chạy trong lifespan
- [ ] Mỗi event ghi vào `EventLog` (event_type, payload, created_at)
- [ ] Gọi các handler đã subscribe
- [ ] Handler fail không crash dispatcher (log + skip)
- [ ] Event types: `SEND_MESSAGE`, `OPEN_CHAT`, `CLOSE_CHAT`, `MEMORY_REFRESH`, `OPEN_AI`
- [ ] Test E2E: gửi message → EventBus ghi EventLog → handler nhận

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
