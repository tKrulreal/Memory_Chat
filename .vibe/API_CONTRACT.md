# MemoryChat API Contract

This document serves as the single source of truth for the frontend and mobile clients integrating with the MemoryChat backend.

## 1. Authentication
All protected routes require a Bearer token in the `Authorization` header.

### Endpoints
- `POST /api/v1/auth/register` (body: `email`, `password`, `full_name`) -> returns `UserResponse`
- `POST /api/v1/auth/login` (body: `email`, `password`) -> returns `{"access_token": "...", "token_type": "bearer"}`
- `GET /api/v1/auth/me` -> returns `UserResponse`
- `POST /api/v1/auth/ws-ticket` -> returns `{"ticket": "..."}` for WebSocket authentication.

## 2. Global Error Shape
Any client error (4xx) or server error (5xx) is returned as a JSON object with this shape:
```json
{
  "error": "Error Type",
  "message": "Human readable details"
}
```
*Note for Validation Errors (422):* The `message` field contains a comma-separated list of issues, e.g., `"body.email: value is not a valid email address"`.

## 3. Pagination Semantics

### Standard Offset Pagination
For endpoints like `/api/v1/direct-conversations` and `/api/v1/connection-requests`:
- Query params: `page` (1-indexed), `limit` (default 20, max 100).
- Response shape:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 5
  }
}
```

### Cursor Pagination (Messages)
For real-time data like `/api/v1/direct-conversations/{id}/messages`:
- Query params: `before_id` (UUID) or `before_created_at` (ISO datetime), `limit` (max 50).
- Response shape:
```json
{
  "data": [...],
  "pagination": {
    "has_next": true,
    "limit": 50
  }
}
```

## 4. Message Shape
```json
{
  "id": "uuid",
  "conversation_id": "uuid",
  "sender_user_id": "uuid",
  "content": "string",
  "created_at": "ISO-8601 string",
  "deleted_at": "ISO-8601 string | null",
  "client_message_id": "string | null"
}
```
*Note:* A recalled message has `deleted_at` set and its `content` is scrubbed by the backend to `"This message was recalled."`.

## 5. WebSocket Protocol

### Connection
- **URL**: `ws://<host>/ws`
- **Auth**: Send a `{ "type": "AUTH", "ticket": "..." }` packet immediately upon connection. 

### Keep-Alive (Heartbeat)
- **Client to Server**: The client MUST send a `{ "type": "PING" }` packet every 30 seconds.
- **Server to Client**: The server replies with `{ "type": "PONG" }`.
- *Failure to send PING within 65 seconds will result in the server forcefully terminating the connection (code 1011).*

### Core Events (Server to Client)

#### `NEW_MESSAGE`
Dispatched when a message is sent in any conversation the user is part of.
```json
{
  "type": "NEW_MESSAGE",
  "id": "uuid",
  "conversation_id": "uuid",
  "sender_user_id": "uuid",
  "content": "...",
  "created_at": "..."
}
```

#### `MESSAGE_RECALLED`
Dispatched when a user recalls their message.
```json
{
  "type": "MESSAGE_RECALLED",
  "conversation_id": "uuid",
  "message_id": "uuid",
  "deleted_at": "ISO-8601 string"
}
```

#### `TYPING` (Upcoming)
```json
{
  "type": "TYPING",
  "conversation_id": "uuid",
  "user_id": "uuid",
  "is_typing": true
}
```
