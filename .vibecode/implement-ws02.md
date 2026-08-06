# WS-02 Implementation

## API Surface

- `GET|POST /api/v1/contacts`
- `GET|PUT|DELETE /api/v1/contacts/{contact_id}`
- `GET|POST /api/v1/conversations`
- `GET|PATCH|DELETE /api/v1/conversations/{conversation_id}`
- `GET|POST /api/v1/conversations/{conversation_id}/messages`
- `GET|DELETE /api/v1/messages/{message_id}`
- `WS /ws/chat/{conversation_id}?token={jwt}`

All identifiers are UUIDs. List responses use `{data, pagination}`.

## Architecture

- `src/schemas/`: API DTOs, enum types, ORM aliases, and pagination envelope.
- `src/repositories/`: owner-filtered Contact, Conversation, and Message queries.
- `src/services/`: constructor-injected services and business rules.
- `src/events/`: typed events, queue dispatcher, durable EventLog writes, and handler failure isolation.
- `src/ws/`: connection manager keyed by conversation UUID.
- `src/api/ws.py`: JWT query-token authentication, ownership validation, persistence, event publication, and broadcast.

## Important Decisions

- Public DTO names remain `name`, `avatar_url`, `role`, and `last_message_at`; Pydantic aliases map them to existing ORM fields.
- HTTP and WebSocket users may submit only `USER` messages; AI/contact messages must be produced by trusted backend workflows.
- Browser WebSockets use a query token because browser APIs cannot set arbitrary Authorization headers.
- Event persistence occurs before handler invocation. Event publication follows successful message/conversation database commits.
