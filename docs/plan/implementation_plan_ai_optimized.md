# Implementation Plan --- Website Fixes & AI Improvements

## Goal

Implement the 6 requested fixes with minimal changes, clear validation,
and no unnecessary refactoring. Prioritize correctness, consistency with
the existing architecture, and production-safe behavior.

## General AI Rules

-   Inspect the existing code, models, APIs, and database structure
    before changing anything.
-   Reuse existing patterns/services/components whenever possible.
-   Do not introduce duplicate logic or unnecessary dependencies.
-   Keep changes scoped to the requested features.
-   Preserve existing behavior unless the plan explicitly changes it.
-   After implementation, run relevant tests/build/lint checks and fix
    regressions.
-   Report changed files, important decisions, validation results, and
    any remaining risks briefly.

------------------------------------------------------------------------

## 1. Fix AI Copilot Vector Search --- Critical

**Problem:** `QdrantClient.search()` is unavailable in the current
`qdrant-client` version.

**Tasks:** - Update `src/services/vector_store.py`. - Replace
`.search()` with the supported `query_points()` API. - Adapt result
parsing to the current Qdrant response structure. - Preserve the
existing search parameters, filtering, scoring, and returned context.

**Done when:** - AI Copilot search no longer raises the
`QdrantClient.search` error. - Relevant vector results are returned
correctly. - Existing fallback/error handling still works.

------------------------------------------------------------------------

## 2. Fix Chat "Unread" Filter --- High

**Problem:** The `Unread` button is currently non-functional.

**Tasks:** - Add `activeFilter` state in
`frontend/components/layout/chat-list-panel.tsx`. - Support at least
`all` and `unread`. - When `unread` is active, show only conversations
where `unread_count > 0`. - Keep existing search/sort behavior intact.

**Done when:** - Clicking `Unread` immediately filters the list. -
Switching back to `All` restores the full list. - No regression to
existing chat interactions.

------------------------------------------------------------------------

## 3. AI Tag Suggestions & Validation --- Medium

**Goal:** Tags must come only from the predefined global tag list.

**Tasks:** - Add `GET /api/v1/tags` using the existing tag/settings data
source. - Update `frontend/components/chat/contact-tags-card.tsx`. - Add
autocomplete suggestions from the global tag list. - Validate tags on
both frontend and backend. - Reject tags that are not predefined. - Fix
the tag `X` button so it calls the correct `DELETE` endpoint and updates
the UI.

**Done when:** - Users can discover valid tags through autocomplete. -
Invalid/manual tags are rejected by the backend. - Adding/removing valid
tags works correctly. - No duplicate tag logic is introduced.

------------------------------------------------------------------------

## 4. AI Profile Read Privacy --- Medium

**Goal:** Let users prevent AI matchmaking from reading their profile.

**Tasks:** - Add `Setting.ai_read_profile: bool = True` in
`src/models/user.py`. - Update `src/schemas/settings.py`. - Create the
required database migration. - Add the toggle to
`frontend/app/(app)/settings/page.tsx`. - Update `RecommendationAgent`
to check this setting before reading profile data.

**Behavior:** - `True`: existing matchmaking behavior. - `False`: AI
must not retrieve/use the user's profile for matchmaking.

**Done when:** - Setting persists correctly. - UI reflects the saved
value. - Recommendation logic respects the setting. - Default behavior
remains unchanged for existing users.

------------------------------------------------------------------------

## 5. Configurable AI Memory Refresh --- Medium

**Goal:** Allow users to control how often AI memory is refreshed.

**Setting values:** - `realtime` - `5_mins` - `daily`

**Tasks:** - Add `Setting.ai_memory_refresh_interval`. - Update schema +
migration. - Add a selector to the Settings UI. - Use the existing
`MemoryAgent.process` implementation. - Add/extend `APScheduler` to
process users according to their selected interval. - Avoid processing
the same user multiple times within the configured interval. -
`realtime` keeps the current immediate-processing behavior.

**Important:** - Do not create a second memory-processing pipeline. -
Scheduler failures must not break normal API/message processing.

**Done when:** - Each interval produces the expected behavior. - Memory
processing is not duplicated. - Scheduler can safely start/stop with the
FastAPI application.

------------------------------------------------------------------------

## 6. Daily Potential-Match Notification --- Low

**Goal:** Give users one consolidated daily notification instead of
multiple match alerts.

**Tasks:** - Add a daily `APScheduler` job. - Find pending
recommendations generated within the previous 24 hours. - Group results
by user. - Create one `Notification` per user only when matches exist. -
Use existing notification models/services where possible. - Prevent
duplicate daily notifications.

**Example:** `You have 3 new potential matches to review today.`

**Done when:** - Users receive at most one summary notification per
daily run. - Users with no new matches receive nothing. - Re-running the
job does not create duplicates.

------------------------------------------------------------------------

## Implementation Order

1.  Vector search bug
2.  Unread filter
3.  Tags
4.  AI profile privacy
5.  Memory refresh
6.  Daily match notification

Complete and validate each item before moving to the next.

## Final Validation

After all changes:

-   Run backend tests.
-   Run frontend lint/typecheck/build.
-   Run database migrations against a clean/test database.
-   Verify API behavior for every new/changed endpoint.
-   Verify Settings persistence and UI state.
-   Verify scheduler startup/shutdown and duplicate prevention.
-   Verify existing chat, recommendation, memory, and notification
    flows.

## Open Decisions

Only ask for clarification if the existing codebase cannot determine the
correct behavior.

Otherwise use these defaults: - Daily memory refresh: run once per day
using the application's scheduler time. - Daily match notification: one
consolidated in-app notification; no email unless explicitly requested.
