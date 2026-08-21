# Implementation Plan — AI Hub & Test Data

## Goal

Implement 2 tasks:

1. Fix `AI Rules & Configuration` so it is **per-user**, not Admin/Global.
2. Create a repeatable seed script for realistic test users and data for AI Matchmaker.

Do not refactor unrelated features.

---

# 1. AI Rules & Configuration — Per User

## Requirement

`AI Rules & Configuration` belongs to each individual user.

Example:

```text
User A → AI Config A
User B → AI Config B
User C → AI Config C
```

Users must only read/update **their own** configuration.

This is NOT:

```text
Admin → Global AI Config → All users
```

Do not introduce Admin permission for this feature.

## Backend

Inspect the existing implementation first, especially:

```text
src/api/v1/tags.py
src/models/
src/services/
src/schemas/
```

The current implementation appears to restrict access using:

```text
@admin.com
```

Replace this approach with ownership based on:

```text
current_user.id
```

### Requirements

- Authenticated user can read their own AI Rules & Configuration.
- Authenticated user can update their own configuration.
- User A cannot read/update User B's configuration.
- Unauthenticated requests → `401`.
- Accessing another user's configuration → `403` or `404`, following existing project conventions.
- Do not hard-code any email as administrator.
- Do not remove authorization checks.
- Reuse the existing user/authentication architecture.

If the current database stores AI configuration globally, modify it minimally so configuration is associated with `user_id`.

Use a uniqueness constraint where appropriate:

```text
(user_id, config_key)
```

so one user cannot accidentally have duplicate configuration entries.

## Frontend

Modify the existing AI Hub implementation.

Requirements:

- `/ai-hub` loads the current user's configuration.
- Display the user's own AI Rules & Configuration.
- Save changes through the authenticated user's API.
- Do not expose an admin selector or global-user selector.
- Handle loading and API errors correctly.

### Verification

Test with at least two users:

```text
User A
  → sees Config A
  → edits Config A

User B
  → sees Config B
  → does not see Config A
```

---

# 2. Test Data Seeder

Create:

```text
scripts/seed_data.py
```

The script must use the project's existing:

- database session
- models
- password hashing
- connection logic
- conversation logic
- message logic

Do not duplicate existing business logic unnecessarily.

---

## 2.1 Users

Read the provided test accounts from the existing account list/file.

For each account:

```text
name
email
password
```

Create the user if it does not exist.

Passwords must use the project's existing password hashing mechanism.

Never store plaintext passwords in the database.

### Idempotency

Running:

```bash
python scripts/seed_data.py
```

multiple times must not create duplicate users.

Existing users should be reused.

---

# 3. User Profiles

Create/update a profile for every seeded user using fields supported by the existing model.

Examples:

```text
bio
gender
phone
profession
company
location
skills
interests
looking_for
offering
```

Use **fictional Vietnamese test data**.

Do not use real people's private information.

Each user should have different but meaningful information.

---

# 4. AI Tags

Seed meaningful tags for the users based on their profile/interests.

Examples:

```text
AI
Backend
Frontend
Python
Java
Gaming
Music
Business
Design
Data
```

Do not assign identical tags to every user.

Create overlapping interests between some users so the AI Matchmaker has meaningful matching signals.

Respect the existing tag limits and uniqueness rules.

---

# 5. Connections

Create a realistic connection network.

Requirements:

- Each user should have approximately 5 connections where possible.
- Never connect a user to themselves.
- Never create duplicate connections.
- Respect the existing connection status/business rules.
- Prefer existing connection services instead of directly bypassing business logic.

The network should not simply connect everyone with everyone.

---

# 6. Conversations & Messages

Create/reuse direct conversations between suitable connected users.

For each conversation:

```text
User A ↔ User B
```

there must be exactly one direct conversation.

Add approximately:

```text
5–10 messages
```

per seeded conversation.

Messages should be **intentional and related to the users' profiles/tags**, not meaningless random text.

Example:

```text
Backend Developer ↔ AI Developer
→ discuss Python
→ discuss FastAPI
→ discuss AI projects
```

Other conversations can cover:

- programming
- AI
- career
- gaming
- music
- business
- hobbies

Use different conversations/topics.

Messages must have realistic chronological timestamps.

Use the existing Message model/service.

---

# 7. AI Matchmaker Data Quality

The seed data must provide useful signals for AI Matchmaker.

Each user should have:

```text
Profile
+ Skills
+ Interests
+ Tags
+ Connections
+ Conversation history
```

Some users should have strong similarities.

Some users should have partial similarities.

Some users should have weak similarities.

This allows the Matchmaker to produce meaningful recommendations instead of every user receiving the same result.

---

# 8. Database Safety

Use transactions where appropriate.

If a critical seed operation fails:

```text
rollback
```

Do not delete existing data automatically.

If reset functionality is required, make it explicit:

```bash
python scripts/seed_data.py --reset
```

Reset must never be the default.

---

# 9. Verification

## AI Hub

Test:

```text
User A → Config A
User B → Config B
```

Verify User A cannot access User B's configuration.

Verify there is no dependency on:

```text
@admin.com
specific email
Admin role
```

for normal AI Rules access.

## Seeder

Run:

```bash
python scripts/seed_data.py
```

Verify:

- test users created
- login works
- profiles exist
- tags exist
- connections exist
- conversations exist
- messages exist

Run the script a second time.

Expected:

```text
No duplicate users
No duplicate connections
No duplicate conversations
No duplicate seed data
```

## AI Matchmaker

Verify seeded profile/tag/chat data is available to the existing Matchmaker and produces meaningful recommendations.

---

# 10. Implementation Order

```text
1. Inspect current AI Rules/auth/database implementation
2. Change AI Rules from Admin/Global → per-user
3. Add/update database migration if required
4. Update backend API/service/schema
5. Update AI Hub frontend
6. Test User A/User B isolation
7. Inspect existing seed/model/business logic
8. Implement seed_data.py
9. Seed users/profiles/tags
10. Seed connections/conversations/messages
11. Run seed twice and verify idempotency
12. Test AI Matchmaker
13. Run existing tests/build
```

# Definition of Done

- [ ] AI Rules & Configuration is per-user.
- [ ] No `@admin.com` authorization remains for this feature.
- [ ] No hard-coded personal email is used.
- [ ] User A cannot access User B's configuration.
- [ ] AI Hub correctly loads/saves the current user's configuration.
- [ ] Seed script creates all required test data.
- [ ] Passwords are securely hashed.
- [ ] Seed script is idempotent.
- [ ] No duplicate connections/conversations are created.
- [ ] Seed conversations contain meaningful profile-related content.
- [ ] AI Matchmaker has useful data to analyze.
- [ ] Existing tests/build pass.