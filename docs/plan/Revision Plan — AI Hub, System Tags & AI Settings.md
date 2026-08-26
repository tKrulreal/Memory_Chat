# Revision Plan — AI Hub, System Tags & AI Settings

## 1. System Tags

### Remove Categories
- Remove the Tag Category system and its dropdown (`Skill`, `Interest`, etc.).
- All tags use one flat global System Tags repository.
- Category must no longer be required by the frontend, backend, or API.

### User-Created Tags
- Users can create any non-empty custom tag.
- Trim whitespace and prevent duplicate active tags.
- User-created tags become active immediately.
- User-created tags are **not affected by the AI tag limit**.

### Tag Validation
- Active chat tags must exist in the global active System Tags repository.
- AI suggestions must not automatically become active System Tags.
- Use normalized tag names for duplicate detection.

### Delete Tags
- Add an `X` delete action to every active tag pill in AI Hub.
- Deleting a tag removes it from the active System Tags repository.
- **Do NOT cascade-delete historical references.**
- Historical conversations/classifications must remain intact.
- Prefer soft-delete/inactive status if required by the existing schema.

---

# 2. AI Tagging

### AI Tag Limit
- Add a configurable **Maximum AI Tag Suggestions** setting.
- User enters the value using a numeric keyboard input.
- The value must be persisted.
- Validate on both frontend and backend.
- The limit applies only to AI-generated suggestions.
- Backend must enforce the limit.

Example:

```text
Limit = 3

AI Tag #1 → allowed
AI Tag #2 → allowed
AI Tag #3 → allowed
AI Tag #4 → blocked
```

### AI Approval Flow

AI-generated tags must follow:

```text
AI Suggestion
      ↓
   PENDING
   ↙     ↘
APPROVE  REJECT
   ↓       ↓
ACTIVE   DISCARDED
```

Rules:

- AI suggestions start as `pending`.
- Pending tags are NOT active System Tags.
- User must explicitly approve a suggestion.
- Approving an existing active tag must reuse it instead of creating a duplicate.
- Rejecting a suggestion must not create an active tag.

### Pending UI

Display pending suggestions separately:

```text
Pending AI Suggestions

Docker       [Approve] [Reject]
Spring Boot  [Approve] [Reject]
```

---

# 3. AI Settings

Rename:

```text
AI Rules & Configuration
```

to:

```text
AI Settings
```

## AI Feature Toggles

The settings control **AI features**, NOT underlying models such as Gemma/Qwen/Llama.

Example:

```text
AI Copilot          [ ON/OFF ]
AI Recommendation   [ ON/OFF ]
AI Memory           [ ON/OFF ]
AI Tagging          [ ON/OFF ]
```

Requirements:

- Each feature has an independent toggle.
- Disabled features must not execute their AI workflow.
- Backend must respect the disabled state.
- Settings must persist across sessions.
- Purpose: allow users to disable unnecessary AI functionality and reduce token usage.
- The exact feature list should match AI features actually implemented in the application.

---

# 4. Memory Settings

Add:

```text
Memory Context Timeframe
```

Allowed values:

```text
1 week
1 month
3 months
6 months
1 year
```

Requirements:

- Dropdown only.
- Persist the selected value.
- Backend must use the selected timeframe.
- If AI Memory is disabled, memory synthesis must not execute.

---

# 5. Settings Structure

AI Settings should contain:

```text
AI Settings
│
├── AI Features
│   ├── AI Copilot
│   ├── AI Recommendation
│   ├── AI Memory
│   └── AI Tagging
│
├── AI Tagging
│   └── Maximum AI Tag Suggestions [number]
│
└── Memory
    └── Memory Context Timeframe [dropdown]
```

---

# 6. Backend Requirements

Backend must enforce:

- No Tag Categories.
- No duplicate active tags.
- Valid active System Tags for chat classifications.
- AI tag limit.
- AI suggestions start as `pending`.
- Approval required before activation.
- AI feature enabled/disabled states.
- Memory timeframe validation.
- Tag deletion must NOT cascade historical references.

Frontend validation alone is insufficient.

---

# 7. Verification Checklist

### System Tags
- [ ] Category dropdown removed.
- [ ] Arbitrary custom tags can be created.
- [ ] Duplicate active tags are prevented.
- [ ] Every active tag has delete action.
- [ ] Deleting a tag preserves historical references.

### AI Tagging
- [ ] User can configure AI tag limit.
- [ ] Limit persists after reload.
- [ ] Backend enforces the limit.
- [ ] AI suggestions start as pending.
- [ ] Pending tags are not active.
- [ ] Approve activates/reuses the tag.
- [ ] Reject does not activate the tag.

### AI Settings
- [ ] Section renamed to `AI Settings`.
- [ ] AI features can be independently enabled/disabled.
- [ ] Disabled features do not execute AI workflows.
- [ ] Settings persist.
- [ ] AI tag limit is configurable.
- [ ] Memory timeframe contains exactly the five required options.
- [ ] Memory timeframe persists and is used by AI Memory.

### Regression
- [ ] Existing conversations remain intact.
- [ ] Historical tag references remain intact.
- [ ] Existing AI functionality still works when enabled.
- [ ] No unrelated functionality is broken.