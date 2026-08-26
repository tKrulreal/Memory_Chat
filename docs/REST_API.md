# MemoryChat REST API Guide

This document outlines the core REST API endpoints required to implement the Mobile application. All endpoints (except Auth) require an `Authorization: Bearer <token>` header.

## Base URL
`https://yourdomain.com/api/v1`

## 1. Authentication

### Register
- **URL:** `POST /auth/register`
- **Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```
- **Response (200 OK):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

### Login
- **URL:** `POST /auth/login`
- **Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```
- **Response (200 OK):**
```json
{
  "access_token": "jwt.token.string",
  "token_type": "bearer"
}
```

### Get WebSocket Ticket
- **URL:** `POST /auth/ws-ticket`
- **Header:** `Authorization: Bearer <token>`
- **Response (200 OK):**
```json
{
  "ticket": "one-time-uuid-string"
}
```

## 2. Connections (Peer-to-Peer)

### Send Connection Request
- **URL:** `POST /connections/`
- **Header:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "receiver_id": "uuid-of-other-user"
}
```
- **Response (200 OK):**
```json
{
  "id": "uuid",
  "status": "pending",
  "created_at": "date"
}
```

### Accept / Reject Request
- **URL:** `PUT /connections/{connection_id}`
- **Body:**
```json
{
  "status": "accepted" // or "rejected"
}
```

## 3. Messages

### Get Messages (Cursor Pagination)
- **URL:** `GET /messages/?limit=50&cursor={message_id}`
- **Response (200 OK):**
```json
{
  "data": [
    {
      "id": "uuid",
      "content": "Hello",
      "sender_id": "uuid",
      "created_at": "date"
    }
  ],
  "next_cursor": "uuid-or-null"
}
```

## 4. Search & AI

### Smart Search (RAG)
- **URL:** `GET /search/conversations?q={query}`
- **Response (200 OK):**
```json
{
  "results": [
    {
      "message_id": "uuid",
      "content": "Relevant text...",
      "score": 0.85
    }
  ]
}
```

---
*For a complete list of endpoints and exact schema typing, refer to the Swagger UI available at `https://yourdomain.com/docs` when the backend is running.*
