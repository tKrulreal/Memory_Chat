# MemoryChat WebSocket Protocol (Mobile Integration Guide)

This document specifies the exact WebSocket protocol to be implemented by Mobile clients (iOS/Android/Flutter) to interact with MemoryChat in real-time.

## 1. Connection Initialization (Handshake)

Since WebSockets on mobile do not easily support standard HTTP headers or cookies, Authentication is done via a one-time "Ticket".

**Step 1:** Call the REST API to get a Ticket.
- **Endpoint:** `POST /api/v1/auth/ws-ticket`
- **Header:** `Authorization: Bearer <your_access_token>`
- **Response:** `{ "ticket": "uuid-string-..." }`

**Step 2:** Connect to the WebSocket.
- **URL:** `wss://yourdomain.com/ws?ticket=<ticket_from_step_1>`

If the ticket is invalid or expired, the connection is instantly closed with code `4003`.

## 2. Payloads (Client -> Server)

When sending messages to the server, always send a stringified JSON object.

### A. Send Chat Message
Used to send a real-time message to another user.
```json
{
  "type": "chat",
  "content": "Hello! How are you?",
  "receiver_id": "uuid-of-the-recipient",
  "idempotency_key": "uuid-generated-by-mobile-app"
}
```
*Note: `idempotency_key` is mandatory to prevent duplicate messages if the network drops right after sending.*

## 3. Payloads (Server -> Client)

You must listen for the following JSON structures from the server.

### A. Incoming Chat Message
When someone sends a message to you (or your own message is echoed back for UI confirmation).
```json
{
  "type": "chat",
  "message": {
    "id": "uuid-of-message",
    "conversation_id": "uuid-of-conversation",
    "sender_id": "uuid-of-sender",
    "content": "Hello! How are you?",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

### B. Message Recalled
When a user recalls a message, this event is broadcasted. You should instantly hide or mask the content of this message in the UI.
```json
{
  "type": "recall",
  "message_id": "uuid-of-recalled-message",
  "conversation_id": "uuid-of-conversation"
}
```

### C. Error Events
If you send a malformed payload or are unauthorized to perform an action.
```json
{
  "type": "error",
  "error": "Message content cannot be empty",
  "code": "400"
}
```

### D. System Events
General alerts from the server.
```json
{
  "type": "system",
  "content": "Welcome to MemoryChat!"
}
```

## 4. Connection Resilience & Retry Logic

Mobile networks are unstable. Your app **must** implement the following logic:
1. **Ping/Pong:** Respond to server pings to keep the connection alive (most WebSocket libraries handle this automatically).
2. **Exponential Backoff:** If the connection drops, do not immediately hammer the server. Reconnect using exponential backoff (1s, 2s, 4s, 8s...).
3. **New Ticket:** If you are disconnected, you **must** fetch a new `ws-ticket` from the REST API before attempting to reconnect. Tickets cannot be reused.
4. **Offline Queue:** If the user sends a message while offline, queue it locally, and send it once reconnected. (The backend's `idempotency_key` ensures it won't be saved twice).
