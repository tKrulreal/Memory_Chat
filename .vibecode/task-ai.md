# AI Task Status

## WS-02 Chat System

- [x] TASK-CHAT-01: schemas, validation, ORM serialization, pagination DTOs.
- [x] TASK-CHAT-02: authenticated Contact CRUD.
- [x] TASK-CHAT-03: authenticated Conversation CRUD and lifecycle events.
- [x] TASK-CHAT-04: Message CRUD and conversation side effects.
- [x] TASK-CHAT-05: WebSocket chat, connection manager, heartbeat, reconnect, two-client test.
- [x] TASK-CHAT-06: EventBus queue, EventLog persistence, dispatcher lifecycle, and handler isolation.
- [x] WS-01 integration: register/login JWT workflow through Contact, Conversation, Message, and EventLog.

## Deferred

- [ ] Subscribe the WS-03 Memory Worker to `SEND_MESSAGE` after that worker exists.
- [ ] Install frontend dependencies and run `npm run build`.
- [ ] Resolve repository-wide Ruff violations outside WS-02 scope.
