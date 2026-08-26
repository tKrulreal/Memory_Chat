# Implementation Plan --- Personal AI Tags & AI Hub

## Goal

-   Convert `Tag` from global/system tags to user-owned personal tags.
-   Make **AI Hub** the single place for AI-related settings and
    personalization.
-   Keep unrelated account/UI settings in `/settings`.
-   Update the **existing PostgreSQL database running in Docker** in
    place.
-   Preserve existing data and behavior unless explicitly changed.
-   Avoid unnecessary refactoring.

------------------------------------------------------------------------

## 1. Database --- Existing Docker PostgreSQL

The project already uses a PostgreSQL database running in Docker.

**This database is the source of truth. Do not create a new database.**

### Migration rules

-   Modify the existing Docker PostgreSQL database in place.
-   Do not reset, recreate, or replace the PostgreSQL container.
-   Do not delete existing data automatically.
-   Use the existing Alembic migration system for all schema changes.
-   Inspect the current schema and existing data before migration.
-   Apply migrations to the currently configured Docker database.
-   Verify schema and data after migration.
-   If existing data cannot be migrated safely, stop and report the
    issue instead of guessing.

------------------------------------------------------------------------

## 2. Personal AI Tags --- Backend

Update `src/models/tag.py`.

### Schema

-   Add `user_id` to `Tag`.
-   Remove global uniqueness on `name`.
-   Add unique constraint: `(user_id, name)`.
-   Keep `user_tags` relationships compatible with the existing system.

Result:

``` text
User A
├── Developer
└── Gamer

User B
├── Developer
└── Music
```

The same tag name may exist for different users, but every tag belongs
to exactly one user.

### API

Update `src/api/v1/tags.py`.

-   `GET /api/v1/tags`
    -   Return only tags owned by `current_user`.
-   `POST /api/v1/tags`
    -   Create the tag for `current_user`.
-   `DELETE /api/v1/tags/{tag_id}`
    -   Verify ownership before deletion.
-   Never allow a user to read, modify, or delete another user's tag.

### Data migration

Before changing the schema:

-   Inspect existing `Tag` and `user_tags` data.
-   Determine whether every existing tag can be mapped to an owner.
-   If ownership can be derived safely, migrate the data.
-   If ownership cannot be determined safely, stop and report the
    affected data.
-   Never silently assign ownership or delete data.

After migration:

-   Verify existing users/tags/user_tags.
-   Verify the new `(user_id, name)` constraint.
-   Verify tag CRUD and user isolation.

------------------------------------------------------------------------

## 3. AI Hub --- Central AI Configuration

Update:

`frontend/app/(app)/ai-hub/page.tsx`

AI Hub becomes the single location for:

-   Personal AI Tags
-   AI behavior/settings
-   AI memory settings
-   AI privacy settings

### AI Tags UI

Rename:

`System Tags` → `My AI Tags`

The UI should clearly communicate that these are the user's personal AI
preferences/personality/rules.

Use the existing tag API.

Only show tags belonging to the current user.

------------------------------------------------------------------------

## 4. Move AI Settings into AI Hub

Move these settings from `/settings` into AI Hub:

-   `ai_enabled`
-   `ai_read_profile`
-   `ai_memory_refresh_interval`
-   `ai_memory_window`

Requirements:

-   Use the existing backend `Setting` model/API.
-   Do not create a second settings storage system.
-   Do not duplicate the same setting UI in both pages.
-   Existing setting values must remain intact after migration.

------------------------------------------------------------------------

## 5. AI Memory Window

Replace the free-text input with a fixed dropdown.

Allowed values:

``` text
1 day
1 week
1 month
3 months
6 months
1 year
```

Use stable backend values, for example:

``` text
1d
1w
1m
3m
6m
1y
```

Requirements:

-   Store machine-readable values.
-   Display human-readable labels.
-   Validate values on the backend.
-   Reject unsupported values.
-   Preserve existing valid values where possible; do not silently reset
    user settings.

------------------------------------------------------------------------

## 6. AI Memory Refresh

Keep:

``` text
realtime
5_mins
daily
```

Use the existing `MemoryAgent.process`.

### Behavior

``` text
realtime
Message → MemoryAgent.process()

5_mins
Messages → pending/dirty user → scheduler → MemoryAgent.process()

daily
Messages → pending/dirty user → daily scheduler → MemoryAgent.process()
```

Requirements:

-   Do not create a second memory-processing pipeline.
-   Avoid processing the same user multiple times for one interval.
-   A user with many messages during one interval should be processed
    once, not once per message.
-   Scheduler failures must not break normal message/API processing.
-   Respect each user's selected interval.
-   Preserve existing `realtime` behavior.

A simple `pending/dirty` mechanism may be used if compatible with the
existing architecture.

------------------------------------------------------------------------

## 7. AI Profile Privacy

`ai_read_profile` controls whether recommendation logic may use the
user's profile.

``` text
true  → profile may be used
false → profile must not be retrieved or used
```

Requirements:

-   Enforce this at the profile retrieval boundary.
-   Inspect the full recommendation flow to ensure the profile is not
    loaded before the setting is checked.
-   Do not rely only on the final AI prompt/agent instruction.
-   Default remains `true` for existing users.
-   Preserve normal recommendation behavior when enabled.

------------------------------------------------------------------------

## 8. Clean Up `/settings`

Update:

`frontend/app/(app)/settings/page.tsx`

Remove AI settings moved to AI Hub:

-   `ai_enabled`
-   `ai_read_profile`
-   `ai_memory_refresh_interval`
-   `ai_memory_window`

Keep unrelated account/UI settings in `/settings`.

### Theme

Theme is a UI/account preference, not an AI setting.

-   Remove Theme only if it is currently inside the AI customization
    section.
-   If Theme already exists elsewhere in `/settings`, leave it
    unchanged.
-   Do not create a new theme system.

------------------------------------------------------------------------

## 9. API / UI Validation

### Tags

-   User A cannot see User B's tags.
-   Same tag name is allowed for different users.
-   Duplicate tag names are rejected for the same user.
-   Users can delete only their own tags.
-   UI updates immediately after add/delete.

### AI Settings

-   AI Hub loads current values.
-   Changes persist after page reload.
-   `/settings` has no duplicate AI settings.
-   Backend rejects invalid values.

### Memory

-   `ai_memory_window` accepts only allowed values.
-   `ai_memory_refresh_interval` accepts only:
    -   `realtime`
    -   `5_mins`
    -   `daily`
-   Selected values persist correctly.
-   Scheduler behavior matches the selected interval.
-   No duplicate memory processing occurs.

### Privacy

-   `ai_read_profile=false` prevents profile retrieval/use during
    matchmaking.
-   `ai_read_profile=true` preserves current behavior.

### Database

-   Migration runs successfully against the existing Docker PostgreSQL
    database.
-   Existing data remains intact unless a safe, explicitly defined
    migration is required.
-   Application starts successfully against the migrated database.
-   No new database/container is created.

------------------------------------------------------------------------

## Implementation Order

1.  Inspect existing Docker PostgreSQL schema and data
2.  Update Tag model + Alembic migration
3.  Apply migration to the existing Docker database
4.  Update Tag API ownership/isolation
5.  Update AI Hub Tags UI
6.  Move AI settings into AI Hub
7.  Implement Memory Window validation/dropdown
8.  Enforce Profile Privacy
9.  Implement/verify Memory Refresh behavior
10. Remove duplicated AI UI from `/settings`
11. Run tests, lint, typecheck, and build
12. Verify the complete end-to-end flow

------------------------------------------------------------------------

## AI Execution Rules

-   Inspect the existing code, database schema, migrations, APIs, and UI
    before changing anything.
-   Use the existing Docker PostgreSQL database as the source of truth.
-   Use Alembic for schema changes.
-   Never create/reset/replace the existing database or PostgreSQL
    container.
-   Never silently delete or rewrite existing data.
-   Reuse existing models, APIs, services, agents, schedulers, and UI
    patterns.
-   Do not create duplicate settings storage or memory pipelines.
-   Do not refactor unrelated code.
-   Keep changes limited to this plan.
-   If a safe migration cannot be determined from the existing
    data/code, stop and report the issue.
-   After implementation, report changed files, migration status,
    validation results, and unresolved issues briefly.
