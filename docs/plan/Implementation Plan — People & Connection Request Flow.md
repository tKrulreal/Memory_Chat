# Implementation Plan — People & Connection Request Flow

## 1. Goal

Implement a unified **People + Connection Request** flow.

### Changes

1. Remove `+ New Chat` from the sidebar.
2. Rename `Current Friends` → `People`.
3. Allow searching all registered users.
4. Hide the current authenticated user.
5. Show actions based on relationship state:
   - `none` → **Add Friend**
   - `pending_sent` → **Pending**
   - `pending_received` → **Accept**
   - `friend` → **Chat**
6. Prevent duplicate requests and duplicate conversations.
7. Keep the existing connection-request system as the source of truth.

---

## 2. Relationship States

The backend must determine the relationship.

```text
none
pending_sent
pending_received
friend
```

### Rules

| State | Meaning | Action |
|---|---|---|
| `none` | No relationship | Add Friend |
| `pending_sent` | Current user sent request | Pending |
| `pending_received` | Target user sent request | Accept |
| `friend` | Request accepted | Chat |

Flow:

```text
none
 ├─ Add Friend → pending_sent
 │
 └─ incoming request → pending_received
                         │
                         └─ Accept → friend → Chat
```

The frontend must **not calculate relationship state itself**.

---

## 3. Backend

### User Search API

Modify:

```text
src/api/v1/search.py
```

Add:

```http
GET /api/v1/search/users?q=<query>&limit=20&offset=0
```

Authentication required.

### Search requirements

- Search `full_name` and `email`.
- Case-insensitive.
- Trim query.
- Exclude current user.
- Apply server-side limit.
- Search in the database, not in Python.
- Return deterministic ordering.

### Response

```json
{
  "items": [
    {
      "id": "uuid",
      "full_name": "Nguyen Minh Anh",
      "email": "nguyenminhanh@gmail.com",
      "avatar": null,
      "relation": "none",
      "conversation_id": null
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

`conversation_id` is only required for `friend`.

---

## 4. Relationship Resolution

Create or reuse a single backend service for relationship calculation.

Example:

```text
ConnectionService.get_relationship(
    current_user_id,
    target_user_id
)
```

Resolution order:

```text
accepted connection
    → friend

pending request sent by current user
    → pending_sent

pending request received by current user
    → pending_received

otherwise
    → none
```

Do not duplicate this logic across routers.

---

## 5. Connection Request Rules

Keep the existing:

```http
POST /api/v1/connection-requests
```

### Sending

Backend must reject:

- sending to yourself
- target user not found
- existing friendship
- existing pending outgoing request
- existing pending incoming request

Duplicate requests must return a controlled `409 Conflict`.

Application checks should be backed by database-level integrity where possible.

---

## 6. Accept Request

Reuse the existing accept operation.

When accepting:

```text
pending_received
        ↓
      accept
        ↓
      friend
```

The operation should be transactional.

It must:

1. Validate the request belongs to the authenticated user.
2. Verify the request is still pending.
3. Mark it accepted.
4. Create or retrieve the direct conversation.
5. Ensure only one direct conversation exists between the two users.

Do not blindly create a new conversation every time.

Use the existing conversation architecture where possible.

---

## 7. Frontend API

Modify:

```text
frontend/lib/api/search.ts
```

Add:

```typescript
searchUsers(q, limit?, offset?)
```

Use a strict type:

```typescript
type UserRelation =
  | "none"
  | "pending_sent"
  | "pending_received"
  | "friend";
```

Response type:

```typescript
interface SearchUser {
  id: string;
  full_name: string;
  email: string;
  avatar: string | null;
  relation: UserRelation;
  conversation_id: string | null;
}
```

---

## 8. People Page

Modify:

```text
frontend/app/(app)/connections/page.tsx
```

### UI

Change:

```text
Current Friends → People
Search friends... → Search people...
```

### Empty query

Show existing friends as before.

### Query

When query length is at least 2:

- debounce by ~300ms
- call `searchUsers`
- show global users
- cancel/ignore stale requests

Do not let an older search response overwrite newer results.

---

## 9. Relation Actions

### `none`

Show:

```text
+ Add Friend
```

On success:

```text
none → pending_sent
```

### `pending_sent`

Show:

```text
Pending
```

Disabled.

Do not send another request.

### `pending_received`

Show:

```text
Accept
```

On success:

```text
pending_received → friend
```

### `friend`

Show:

```text
Chat
```

Navigate to the existing conversation.

Do not create another conversation from the frontend.

---

## 10. Loading & Error Handling

Use per-user action loading.

Example:

```text
Add Friend
    ↓
Adding...
```

Do not block the entire People page.

Handle at least:

```text
400 → invalid request
403 → unauthorized
404 → user/request not found
409 → relationship already exists
500 → server error
```

For `409`, refresh the user's relationship instead of leaving stale UI.

---

## 11. Sidebar

Modify:

```text
frontend/components/layout/nav-sidebar.tsx
```

Remove:

- `NewChatModal` import
- `isModalOpen`
- New Chat button
- `NewChatModal` rendering
- related unused state/imports

The connection-first flow becomes:

```text
People
  ↓
Add Friend
  ↓
Accept
  ↓
Chat
```

---

## 12. Security

Never trust relationship information sent by the frontend.

Backend must verify:

### Accept request

```text
request.receiver_id == current_user.id
```

### Conversation

User must actually belong to the conversation.

### Search

Current user must never appear in their own results.

---

## 13. Testing

### Backend

Test:

- search by name
- search by email
- case-insensitive search
- current user excluded
- relationship states returned correctly
- self-request rejected
- duplicate request rejected
- incoming request detected
- unauthorized accept rejected
- accept changes relationship to `friend`
- accepting twice handled safely
- conversation is created/reused exactly once

### Frontend

Test:

- New Chat removed
- People displayed
- empty search shows friends
- global search works
- correct action for every relationship state
- Add Friend → Pending
- Accept → Chat
- Chat opens correct conversation
- stale search responses do not overwrite current results
- API errors recover correctly

---

## 14. Manual E2E Verification

Use three test accounts.

### Scenario A

```text
A searches B
→ Add Friend
→ Pending
```

### Scenario B

```text
B sees A
→ Accept
→ Chat
```

### Scenario C

```text
A clicks Chat
→ correct A ↔ B conversation
```

### Scenario D

Rapidly click Add Friend multiple times.

Expected:

```text
exactly one pending request
```

### Scenario E

A sends request to B.

B attempts to send request to A.

Expected:

```text
Accept
```

not another `Add Friend`.

---

## 15. Implementation Order

### Phase 1 — Backend

1. Inspect existing connection/request models.
2. Implement/reuse relationship resolver.
3. Add `/search/users`.
4. Harden request validation.
5. Ensure accept + conversation creation is transactional.
6. Add backend tests.

### Phase 2 — Frontend

7. Add `searchUsers()`.
8. Add relationship types.
9. Implement People search.
10. Implement relation buttons.
11. Add loading/error handling.
12. Remove New Chat.

### Phase 3 — Verification

13. Run backend tests.
14. Run frontend tests/build.
15. Test multi-account flow.
16. Test duplicate/race scenarios.
17. Rebuild Docker.

```bash
docker compose up -d --build backend frontend
```

---

# Definition of Done

- [ ] New Chat removed.
- [ ] People search works.
- [ ] Current user hidden.
- [ ] Relationship determined by backend.
- [ ] Add Friend works.
- [ ] Duplicate requests prevented.
- [ ] Pending state works.
- [ ] Accept works.
- [ ] Friend state works.
- [ ] Chat opens the correct existing conversation.
- [ ] Duplicate conversations prevented.
- [ ] Unauthorized operations rejected.
- [ ] Backend tests pass.
- [ ] Frontend build/tests pass.
- [ ] Docker rebuild succeeds.