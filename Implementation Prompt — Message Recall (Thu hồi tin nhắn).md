# Implement Message Recall (Thu hồi tin nhắn)

## Objective

Implement a complete **Message Recall** feature for the existing P2P chat system.

Users must be able to recall messages they personally sent. Recall is a **soft delete**: the message remains in the database with `deleted_at` set, but the original content must no longer be displayed in the chat UI.

The feature must work **end-to-end**, including:

- Backend authorization and soft deletion
- WebSocket real-time synchronization
- Frontend state updates
- Recall UI/UX
- Persistence after page reload
- Automated verification

Do **not** redesign the existing chat architecture. Reuse the project's existing message service, WebSocket infrastructure, React Query/state management, API conventions, components, and error-handling patterns.

---

# Phase 1 — Inspect Before Coding

Before modifying anything, inspect the existing implementation.

At minimum, inspect:

### Backend

- Message model
- Message schema / response DTO
- `src/api/v1/messages.py`
- `src/services/message.py`
- Existing message creation endpoint
- Existing message retrieval/list endpoint
- Existing WebSocket implementation
- Existing `NEW_MESSAGE` WebSocket event
- WebSocket connection/participant management
- Existing authorization patterns
- Existing message tests

### Frontend

- `frontend/types/index.ts`
- `frontend/lib/api/messages.ts`
- `frontend/lib/stores/conversation-store.ts`
- `frontend/components/chat/message-bubble.tsx`
- `frontend/components/layout/chat-window.tsx`
- Existing message mutations
- Existing WebSocket event handling
- Existing confirmation/dialog components
- Existing tests

First understand the current architecture and reuse existing patterns.

**Do not create a second WebSocket mechanism, state-management mechanism, or message service if one already exists.**

---

# Phase 2 — Backend

## 2.1 Message model

Use the existing `deleted_at` field.

Do not introduce another deletion flag unless the existing architecture genuinely requires it.

A recalled message should have:

```text
deleted_at != null
```

An active message should have:

```text
deleted_at == null
```

---

## 2.2 Authorization

Only the original sender may recall the message.

For a message:

```text
User A → User B
```

the following must be true:

```text
A → DELETE message   ✅
B → DELETE message   ❌
Other user → DELETE  ❌
```

Authorization must be enforced on the backend.

Do NOT rely on hiding the Recall button in the frontend.

Return the project's existing appropriate authorization/error response for unauthorized recall.

---

## 2.3 Recall service

Modify:

```text
src/services/message.py
```

so `delete_message()` performs a soft delete and returns the updated message.

Expected flow:

```text
validate message
      ↓
validate sender ownership
      ↓
set deleted_at
      ↓
commit transaction
      ↓
refresh/retrieve updated message
      ↓
return updated message
```

The database transaction must succeed **before** the WebSocket event is broadcast.

Do not broadcast a successful recall before the database commit.

---

## 2.4 DELETE endpoint

Modify:

```text
src/api/v1/messages.py
```

The endpoint should:

1. Validate the authenticated user.
2. Validate that the message exists.
3. Validate that the authenticated user owns the message.
4. Soft-delete the message.
5. Commit the database transaction.
6. Retrieve/receive the updated message.
7. Broadcast `MESSAGE_RECALLED` to the participants of the conversation.
8. Return the project's existing appropriate success response.

Reuse the existing WebSocket broadcasting mechanism used by `NEW_MESSAGE`.

Do not introduce a new WebSocket connection or manager.

---

# Phase 3 — WebSocket Event

Introduce:

```text
MESSAGE_RECALLED
```

Use the existing WebSocket event format used by the project.

Prefer sending only the data required by the frontend:

```json
{
  "type": "MESSAGE_RECALLED",
  "conversation_id": "<conversation_id>",
  "message_id": "<message_id>",
  "deleted_at": "<ISO-8601 timestamp>"
}
```

Adapt the exact field naming/serialization to the project's existing WebSocket protocol.

The event must be delivered to both participants of the conversation.

The event must only be emitted after the database update succeeds.

---

# Phase 4 — Message Retrieval / Persistence

Verify the existing message GET/list endpoint correctly exposes `deleted_at`.

After a recalled message is fetched again, the frontend must still know that it was recalled.

Example:

```json
{
  "id": "...",
  "deleted_at": "2026-08-18T..."
}
```

If the current response exposes the original message content after recall, evaluate whether the response should suppress the recalled content.

The important security requirement is:

> A recalled message must never be rendered as active message content by the frontend.

Do not break existing database integrity unnecessarily.

---

# Phase 5 — Frontend API

Modify:

```text
frontend/lib/api/messages.ts
```

Add:

```ts
deleteMessage(messageId: string): Promise<void>
```

or follow the project's existing API abstraction if `conversationId` is genuinely required for cache/state handling.

Call:

```text
DELETE /api/proxy/api/v1/messages/{message_id}
```

Reuse existing authentication, error handling, React Query, and API client conventions.

Do not duplicate API client logic.

---

# Phase 6 — Message Type

Modify:

```text
frontend/types/index.ts
```

Ensure:

```ts
deleted_at: string | null
```

is included in the `Message` type.

Update all relevant fixtures, mocks, constructors, and test data if TypeScript requires them.

Do not use optional `deleted_at` unless the existing API contract genuinely requires it. Prefer an explicit:

```ts
deleted_at: string | null
```

---

# Phase 7 — Conversation Store / WebSocket

Modify:

```text
frontend/lib/stores/conversation-store.ts
```

Handle:

```text
MESSAGE_RECALLED
```

When the event is received:

1. Check the `conversation_id`.
2. Find the corresponding message by `message_id`.
3. Update only that message's `deleted_at`.
4. Preserve the rest of the message state.
5. Trigger the existing reactive update mechanism.

Conceptually:

```text
MESSAGE_RECALLED
       ↓
conversation_id
       ↓
find message_id
       ↓
message.deleted_at = event.deleted_at
       ↓
UI re-render
```

If the message is not currently loaded, do not create a fake message solely from the recall event.

The normal message fetch should provide the correct recalled state later.

---

# Phase 8 — Message Bubble UI

Modify:

```text
frontend/components/chat/message-bubble.tsx
```

## Recalled message

When:

```ts
deleted_at !== null
```

render a generic recalled-message state:

```text
Tin nhắn đã được thu hồi
```

The recalled message must:

- Hide the original text
- Hide images/files/attachments
- Not render active message actions
- Use the existing design system
- Use muted/grayed styling
- Remain visually consistent with the chat UI

Structure the rendering so recalled state takes precedence over normal content rendering:

```text
MessageBubble
    │
    ├── deleted_at != null
    │       └── RecalledMessage
    │
    └── normal message
            ├── text
            ├── image
            ├── file
            └── ...
```

---

# Phase 9 — Recall Action

Only outgoing, non-recalled messages may display the Recall action.

Conditions:

```text
outgoing == true
AND
deleted_at == null
```

Show a small hover action using the project's existing icon/button conventions.

Use an appropriate existing icon such as:

```text
Undo / RotateCcw / Trash
```

Prefer an icon with a tooltip:

```text
Thu hồi
```

Do not add a large button that disrupts the existing chat layout.

---

# Phase 10 — Confirmation UX

Use a small confirmation dialog before recalling.

Recommended copy:

```text
Thu hồi tin nhắn?

Tin nhắn này sẽ được thu hồi khỏi cuộc trò chuyện.

[Hủy] [Thu hồi]
```

Reuse the project's existing Dialog/Modal/AlertDialog component if available.

Do not create a new dialog abstraction if one already exists.

While the recall request is pending:

- Prevent duplicate clicks.
- Show the project's existing loading state if appropriate.
- Handle API failure without changing the message into a recalled state.

Only the successful backend response / WebSocket event should produce the recalled state.

---

# Phase 11 — Chat Window Integration

Modify:

```text
frontend/components/layout/chat-window.tsx
```

Ensure `deleted_at` reaches `MessageBubble`.

Follow the existing component data flow.

Prefer keeping API/mutation logic outside `MessageBubble` if the existing architecture follows a container/presentation pattern.

If the project already uses React Query mutations in components, follow that established pattern instead.

Do not introduce unnecessary architectural changes.

---

# Phase 12 — Important Edge Cases

The implementation must correctly handle:

### Self recall

```text
Sender recalls own message
→ success
```

### Receiver attempting recall

```text
Receiver attempts DELETE
→ rejected by backend
```

### Another user attempting recall

```text
Unauthorized user
→ rejected
```

### Double click

```text
Recall clicked twice
→ only one valid recall
→ no duplicate side effects
```

### Recalling an already recalled message

Handle idempotently or return the project's appropriate conflict/not-found response.

Do not create inconsistent state.

### Realtime update

```text
Browser A recalls message
        ↓
Browser B receives MESSAGE_RECALLED
        ↓
Browser B updates without refresh
```

### Reload

After recalling:

```text
F5
```

the message must still appear as:

```text
Tin nhắn đã được thu hồi
```

and must never revert to the original content.

### Different message types

If supported by the current application:

```text
Text
Image
File
Link
Reply/Quoted message
```

all recalled messages must stop rendering their original content.

---

# Phase 13 — Testing

Do not consider the feature complete merely because the application starts.

Add or update automated tests following the project's existing testing conventions.

At minimum verify:

### Backend

- Sender can recall own message.
- Receiver cannot recall another user's message.
- Unauthorized users cannot recall the message.
- `deleted_at` is persisted.
- Recalling a message does not hard-delete the database row.
- `MESSAGE_RECALLED` is broadcast after successful commit.
- Recalled message remains recalled when fetched again.

### Frontend

- `deleted_at` message renders "Tin nhắn đã được thu hồi".
- Original content is not rendered when recalled.
- Recall action appears only for outgoing active messages.
- Recall action does not appear for incoming messages.
- Recall action does not appear for already recalled messages.
- `MESSAGE_RECALLED` updates the correct message in the conversation store.

### E2E

If Playwright/E2E infrastructure already exists, add a test covering:

```text
User A sends message
        ↓
User A recalls message
        ↓
User A sees "Tin nhắn đã được thu hồi"
        ↓
User B sees "Tin nhắn đã được thu hồi"
        ↓
Reload
        ↓
Both still see recalled state
```

Use the project's existing test setup and test users.

Do not invent a parallel testing framework.

---

# Phase 14 — Verification

Run the appropriate existing checks for both backend and frontend.

At minimum, run the project's available:

```text
- Backend tests
- Frontend tests
- Type checking
- Lint
- E2E tests if available
```

Also manually verify the two-browser realtime flow.

Do not claim the feature is complete if tests fail.

If an existing unrelated test fails, clearly distinguish:

```text
Feature-related failure
vs
Pre-existing/unrelated failure
```

---

# Constraints

1. Do not redesign the existing architecture.
2. Do not introduce a second WebSocket mechanism.
3. Do not introduce a second state-management pattern.
4. Do not hard-delete messages.
5. Do not trust frontend authorization.
6. Do not broadcast before database commit.
7. Do not expose/render recalled message content.
8. Do not modify unrelated features.
9. Reuse existing project conventions and components.
10. Keep the implementation minimal and production-ready.

Before changing a file, inspect its existing implementation and surrounding dependencies.

If the proposed plan conflicts with the existing architecture, **stop and explain the conflict before making a large architectural change**.

---

# Definition of Done

The feature is complete only when all of the following are true:

- [ ] A user can recall their own sent message.
- [ ] The message is soft-deleted using `deleted_at`.
- [ ] Only the sender can recall it.
- [ ] The database update succeeds before WebSocket broadcast.
- [ ] `MESSAGE_RECALLED` is sent to both conversation participants.
- [ ] The sender sees the recalled state immediately.
- [ ] The receiver sees the recalled state in real time without refresh.
- [ ] Reloading the conversation preserves the recalled state.
- [ ] Original text/image/file content is no longer rendered.
- [ ] Recall action only appears for outgoing active messages.
- [ ] Confirmation dialog works correctly.
- [ ] Duplicate recall actions are safely handled.
- [ ] Backend tests pass.
- [ ] Frontend/type/lint checks pass.
- [ ] E2E test passes if E2E infrastructure exists.
- [ ] No unrelated architecture was unnecessarily changed.

---

# Final Report

After implementation, report:

## Changed

List every modified/created file and briefly explain why.

## Behavior

Explain the final recall flow from UI → API → DB → WebSocket → UI.

## Tests

List every command executed and its result.

Example:

```text
pytest                    PASS
npm run lint              PASS
npm run typecheck         PASS
npm run test:e2e          PASS
```

## Manual Verification

Report the result of:

```text
Sender recall
Receiver realtime update
Reload persistence
Unauthorized recall
```

## Issues

If anything could not be verified, state it explicitly.

Do not say "completed successfully" unless the Definition of Done has actually been verified.