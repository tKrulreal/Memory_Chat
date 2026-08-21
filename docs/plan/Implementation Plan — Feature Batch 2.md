# Implementation Plan — Feature Batch 2

## Goal

Implement 6 features for MemoryChat:

1. Message read/unread state
2. User gender & phone
3. Phone-based user search
4. Tag management & AI system settings
5. AI/Copilot settings
6. Connection recommendation notification

Preserve existing architecture and reuse existing models/services/APIs where possible. Do not create duplicate systems.

---

## 1. Read / Unread Messages

### Backend

Modify:

- `src/services/conversation.py`
- `src/schemas/conversation.py`
- `src/api/v1/conversations.py`
- `src/api/v1/messages.py`

Requirements:

- Calculate `unread_count` per conversation for the current user.
- Count messages after `last_read_message_id` where sender != current user.
- Add `unread_count: int` to `ConversationResponse`.
- Add:

```http
POST /api/v1/direct-conversations/{conversation_id}/read
```

- Update/create `ConversationUserState.last_read_message_id`.
- Sending a message should mark the sender's own messages as read.
- Verify the current user belongs to the conversation.

### Frontend

Modify:

- `frontend/lib/api/conversations.ts`
- `frontend/components/layout/chat-list-panel.tsx`
- `frontend/components/layout/chat-window.tsx`

Requirements:

- `Unread` filter uses `unread_count > 0`.
- Unread item: bold name + unread badge + dot.
- Opening a conversation marks it as read.
- Realtime message event updates/invalidate conversation data.
- Avoid duplicate mark-as-read requests where possible.

---

## 2. Gender & Phone

### Backend

Modify:

- `src/models/user.py`
- `src/services/auth.py`
- `src/api/v1/auth.py`
- `src/api/v1/profile.py`

Migration:

```text
alembic/versions/*_add_gender_phone.py
```

Add:

```text
gender: nullable string
phone: nullable string
```

Requirements:

- Existing users remain valid.
- Backfill existing data only if the product explicitly requires it; do not generate fake personal information silently.
- Validate gender against supported values.
- Validate phone format.
- Phone should have an index if used for search.

### Frontend

Modify:

- `frontend/app/(auth)/register/page.tsx`
- `frontend/app/(app)/settings/page.tsx`

Add optional:

- Gender
- Phone number

---

## 3. Phone Search

Modify:

```text
src/api/v1/search.py
frontend/app/(app)/connections/page.tsx
```

Existing:

```http
GET /api/v1/search/users?q=
```

must also search:

```text
full_name
email
phone
```

Requirements:

- Case-insensitive where applicable.
- Exclude current user.
- Keep existing relationship information.
- Search must happen at database level.
- Update placeholder:

```text
Search by name, email or phone...
```

---

## 4. Tags & AI System Configuration

### Backend

Add:

```text
src/models/tag.py
```

Models:

```text
Tag
UserTag
AISystemConfig
```

Requirements:

- `Tag.name` unique.
- `Tag.category`.
- `Tag.is_active`.
- `UserTag(user_id, tag_id)` unique.
- AI config stored centrally.
- Only authorized admin users can create/update global tags and AI configuration.
- Enforce maximum total tags and maximum tags per user on the backend.

Migration:

```text
alembic/versions/*_add_tags_ai_config.py
```

Seed a small default tag set and default AI configuration.

APIs:

```http
GET    /api/v1/tags
POST   /api/v1/tags              # admin
GET    /api/v1/tags/my
POST   /api/v1/tags/my/{tag_id}
DELETE /api/v1/tags/my/{tag_id}

GET    /api/v1/ai-config
PUT    /api/v1/ai-config/{key}   # admin
```

Do not hardcode limits in frontend only.

### Frontend

Add:

```text
frontend/lib/api/tags.ts
```

Modify:

```text
frontend/app/(app)/ai-hub/page.tsx
```

AI Hub should contain:

- Tags
- AI Settings
- Existing Memory content

Users can select/remove their tags within backend-defined limits.

---

## 5. AI / Copilot Settings

### Backend

Add to the existing user settings model/table:

```text
ai_enabled
ai_memory_window
```

Supported windows:

```text
1month
3months
6months
1year
unlimited
```

Migration:

```text
alembic/versions/*_add_ai_settings.py
```

API:

```http
GET   /api/v1/settings
PATCH /api/v1/settings
```

Requirements:

- Existing users receive safe defaults.
- Validate `ai_memory_window`.
- `ai_enabled = false` must prevent AI memory processing.
- Memory processing must respect the selected time window.
- Do not break unrelated settings.

Modify:

```text
src/services/memory.py
src/workers/memory_worker.py
```

### Frontend

Modify:

```text
frontend/app/(app)/settings/page.tsx
frontend/lib/api/profile.ts
```

Add:

- Copilot enabled toggle
- Memory window selector

---

## 6. Connection Recommendation Notification

### Backend

Reuse the existing recommendation system.

Add:

```text
NEW_RECOMMENDATION = "new_recommendation"
```

Modify:

```text
src/events/types.py
src/workers/connection_worker.py
```

When a new `CONNECTION` recommendation is created, publish:

```json
{
  "recommendation_id": "uuid",
  "target_user_name": "...",
  "reason": "..."
}
```

Do not create duplicate recommendations solely for notification purposes.

### Frontend

Add:

```text
frontend/components/notifications/FriendSuggestionToast.tsx
frontend/hooks/useFriendSuggestionNotification.ts
```

Modify:

```text
frontend/components/layout/app-shell.tsx
frontend/lib/ws/
```

Requirements:

- Check pending connection recommendations after login.
- Listen for `new_recommendation` via WebSocket.
- Show avatar, name, reason, View and Dismiss.
- View → `/recommendations`.
- Auto-dismiss after ~8 seconds.
- Show at most once per session using `sessionStorage`.
- Accessible toast (`role="alert"` / appropriate live region).
- Do not show duplicate notifications for the same recommendation.

---

# Implementation Order

## Phase 1 — Database & Backend

1. Add gender/phone migration.
2. Add AI settings migration.
3. Add Tag/UserTag/AI config migration.
4. Update models/schemas.
5. Implement unread count + mark-as-read.
6. Add phone search.
7. Implement settings API.
8. Implement tag APIs + authorization.
9. Update memory processing rules.
10. Add recommendation WebSocket event.

## Phase 2 — Frontend

11. Update TypeScript types/API clients.
12. Implement unread UI and mark-as-read.
13. Add gender/phone to register/settings.
14. Add phone search.
15. Implement AI Hub tags/config.
16. Implement AI settings.
17. Implement recommendation toast.

## Phase 3 — Verification

Test:

- Unread count/filter/mark-as-read.
- Gender/phone persistence.
- Phone search.
- Tag CRUD, permissions and limits.
- AI toggle and memory window.
- Recommendation toast and session deduplication.
- Existing functionality remains intact.

Then run:

```bash
docker compose up -d --build backend frontend
```

Check backend/frontend logs and run the project's existing test suite.

---

# Definition of Done

- [ ] All migrations run successfully without losing existing data.
- [ ] `unread_count` is correct and Unread filter works.
- [ ] Opening a chat marks it read.
- [ ] Gender/phone can be stored and updated.
- [ ] Phone search works.
- [ ] Tags have backend-enforced limits and admin authorization.
- [ ] AI settings persist and affect memory processing.
- [ ] Recommendation toast works for login + WebSocket events.
- [ ] No duplicate requests/tags/notifications are created.
- [ ] Existing features remain compatible.
- [ ] Backend tests pass.
- [ ] Frontend build/tests pass.
- [ ] Docker rebuild succeeds.

---

# Important Constraints

- Reuse existing architecture before introducing new abstractions.
- Backend is the source of truth for permissions, limits and relationship/state logic.
- Never trust frontend-only validation.
- Do not generate fake personal data for existing users unless explicitly required.
- Use database constraints for uniqueness where appropriate.
- Keep changes scoped to these features; avoid unrelated refactoring.
- Before coding, inspect the existing models, services, migrations and APIs and adapt the plan to the actual codebase.