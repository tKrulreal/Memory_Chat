# MemoryChat Frontend Plan

**Version:** 1.0  
**Status:** Approved baseline (editable)  
**Last updated:** 2026-08-15

---

## 1. Decisions (locked for this plan)

| Decision | Choice |
|----------|--------|
| Tech stack | Next.js 15 + React 19 + Tailwind + Zustand + TanStack Query |
| MVP scope | Chat + AI full |
| UI language | English |
| Auth storage | httpOnly cookie (Next.js BFF → FastAPI JWT) |
| Right panel | Collapsible (desktop inline + tablet/mobile drawer) |
| Call button | Placeholder (disabled, “Coming soon”) |
| AI priority | 1) Context bar → 2) Copilot → 3) Recommendations |
| Layout base | Meta Messenger 3-column + MemoryChat nav + green theme |

---

## 2. Scaffold status

The following already exists under `frontend/`:

| Area | Path | Status |
|------|------|--------|
| Design tokens | `app/globals.css`, `tailwind.config.ts` | Done |
| App shell | `components/layout/app-shell.tsx` | Done |
| Nav sidebar | `components/layout/nav-sidebar.tsx` | Done |
| Chat list | `components/layout/chat-list-panel.tsx` | Demo data |
| Chat window | `components/layout/chat-window.tsx` | Demo data |
| Info panel | `components/layout/info-panel.tsx` | Collapsible |
| AI context bar | `components/ai/ai-context-bar.tsx` | Static demo |
| AI recommendation | `components/ai/ai-recommendation-card.tsx` | Empty state |
| Copilot drawer | `components/ai/copilot-drawer.tsx` | Shell only |
| Auth BFF | `app/api/auth/*` | Login cookie flow |
| Middleware | `middleware.ts` | Route protection |
| Stores | `lib/stores/*` | Skeleton |

**Run locally:**

```bash
cd frontend && npm install && npm run dev
```

Backend: `http://localhost:8000` with `CORS_ORIGINS=http://localhost:3000`.

---

## 3. Architecture overview

```
┌──────────┬─────────────┬────────────────────────────┬─────────────────┐
│ NavSidebar│ ChatList   │ ChatWindow                 │ InfoPanel       │
│           │ Panel      │  ├─ ChatHeader             │  ├─ PeerProfile │
│ + New Chat│ Search     │  ├─ AIContextBar  ★        │  ├─ QuickActions│
│ Chats     │ Filters    │  ├─ ConnectionStatus       │  ├─ AIRecCard ★ │
│ Search    │ Items      │  ├─ MessageList            │  └─ Accordions  │
│ AI Hub    │            │  └─ Composer (+ / AI)      │                 │
│ ...       │            │ CopilotDrawer ★ (overlay)  │                 │
└──────────┴─────────────┴────────────────────────────┴─────────────────┘
                              ★ = AI priority features
```

### Data flow

```
Browser → Next.js BFF (/api/*) → FastAPI REST
Browser → WebSocket (/ws/chat?ticket=) ← ws-ticket from BFF
Client state: Zustand (UI, active conversation, optimistic messages)
Server state: TanStack Query (conversations, messages, AI context)
```

---

## 4. Design system reference

Tokens live in `frontend/app/globals.css`.

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-app` | `#0a0a0a` | Main background |
| `--bg-surface` | `#121212` | Sidebars, list |
| `--bg-elevated` | `#1a1a1a` | Incoming bubbles, cards |
| `--bg-input` | `#2a2a2a` | Composer, search |
| `--accent-primary` | `#22c55e` | CTA, active nav, outgoing bubbles |
| `--accent-warning` | `#f97316` | Send reminder |
| `--accent-ai` | `#fef3c7` | Recommendation card |
| `--width-nav` | `220px` | Left nav |
| `--width-chat-list` | `320px` | Conversation list |
| `--width-info-panel` | `300px` | Right panel |

### Responsive behavior

| Breakpoint | Behavior |
|------------|----------|
| `≥1280px` | Full 4-column layout |
| `1024–1279px` | Nav collapses to icon-only |
| `<1280px` | Info panel becomes drawer overlay |
| `<768px` | Future: single-view navigation (list ↔ chat) |

---

## 5. Backend API mapping

### Available today

| Feature | Method | Endpoint |
|---------|--------|----------|
| Register | POST | `/api/v1/auth/register` |
| Login | POST | `/api/v1/auth/login` |
| Current user | GET | `/api/v1/auth/me` |
| WS ticket | POST | `/api/v1/auth/ws-ticket` |
| List conversations | GET | `/api/v1/direct-conversations` |
| Create DM | POST | `/api/v1/direct-conversations` |
| Get conversation | GET | `/api/v1/direct-conversations/{id}` |
| List messages | GET | `/api/v1/direct-conversations/{id}/messages` |
| Send message | POST | `/api/v1/direct-conversations/{id}/messages` |
| Copilot chat | POST | `/api/v1/copilot/chat` |
| Notifications | GET | `/api/v1/notifications` |
| WebSocket | WS | `/ws/chat?ticket=` |

### Required from backend (blockers for AI full)

| Feature | Proposed endpoint | Blocks |
|---------|-------------------|--------|
| User lookup (New Chat) | `GET /api/v1/users?handle=` or `?email=` | FE-012 |
| Assistant context | `GET /api/v1/direct-conversations/{id}/assistant/context` | FE-020 |
| Update context facts | `PATCH /api/v1/direct-conversations/{id}/assistant/context` | FE-021 |
| Recommendations list | `GET /api/v1/assistant/recommendations?conversation_id=` | FE-030 |
| Dismiss recommendation | `POST /api/v1/assistant/recommendations/{id}/dismiss` | FE-031 |
| Send reminder draft | `POST /api/v1/copilot/share` (draft mode) | FE-032 |
| Mark read | `POST /api/v1/direct-conversations/{id}/read` | FE-015 |

---

## 6. Task breakdown (Jira / Linear style)

**Legend**

- **Priority:** P0 (blocker) · P1 (MVP) · P2 (polish)
- **Labels:** `frontend`, `chat`, `ai`, `auth`, `realtime`, `backend-dep`
- **Points:** Fibonacci (1, 2, 3, 5, 8)

---

### Epic E1: Foundation & design system

| ID | Title | Description | Acceptance criteria | Deps | Priority | Points |
|----|-------|-------------|---------------------|------|----------|--------|
| FE-001 | Design tokens & Tailwind setup | CSS variables + Tailwind theme extension | All tokens in `globals.css`; Tailwind colors reference vars; dark theme only | — | P0 | 2 |
| FE-002 | AppShell layout | 4-column responsive shell | Nav + list + chat + collapsible info panel render at 1280px+; no horizontal scroll | FE-001 | P0 | 3 |
| FE-003 | Shared UI primitives | Button, Input, Avatar, Badge, Skeleton | Reusable components in `components/ui/`; consistent radius and accent colors | FE-001 | P1 | 3 |
| FE-004 | Route structure | App Router groups `(app)` / `(auth)` | `/chats`, `/login`, `/register`, placeholder routes for nav items | FE-002 | P0 | 2 |

**Epic exit:** Developer can run `npm run dev` and see full shell with demo chat UI.

---

### Epic E2: Authentication (httpOnly cookie)

| ID | Title | Description | Acceptance criteria | Deps | Priority | Points |
|----|-------|-------------|---------------------|------|----------|--------|
| FE-010 | BFF login route | POST `/api/auth/login` → set httpOnly cookie | Successful login sets cookie; failed login returns 4xx JSON error | — | P0 | 3 |
| FE-011 | BFF logout + me | Logout clears cookie; me proxies `/auth/me` | `/api/auth/logout` clears session; `/api/auth/me` returns user or 401 | FE-010 | P0 | 2 |
| FE-012 | Login / Register pages | Forms wired to BFF | User can register, login, redirect to `/chats`; validation errors shown | FE-010 | P0 | 3 |
| FE-013 | Auth middleware | Protect `(app)` routes | Unauthenticated users redirect to `/login`; authed users skip auth pages | FE-010 | P0 | 2 |
| FE-014 | Auth bootstrap | Load user on app mount | Nav sidebar shows real user name/email from `/api/auth/me` | FE-011, FE-002 | P1 | 2 |
| FE-015 | Logout action | Wire NavSidebar logout | Click logout → POST `/api/auth/logout` → redirect `/login` | FE-011 | P1 | 1 |

**Epic exit:** Full cookie-based auth loop without exposing JWT to `localStorage`.

---

### Epic E3: P2P Chat core

| ID | Title | Description | Acceptance criteria | Deps | Priority | Points |
|----|-------|-------------|---------------------|------|----------|--------|
| FE-020 | API client layer | Typed fetch wrappers + BFF proxy for authenticated calls | `lib/api/conversations.ts`, `messages.ts`; errors normalized | FE-010 | P0 | 3 |
| FE-021 | Conversation list (live) | Replace demo data with TanStack Query | List loads from API; pagination; loading/error states | FE-020 | P0 | 5 |
| FE-022 | New Chat modal | Find user + create DM | Modal with user search; POST conversation; opens new thread | FE-020, **BE user search** | P0 | 5 |
| FE-023 | Message list | Fetch + render messages for active conversation | Cursor/page pagination; group by date; scroll to bottom on open | FE-021 | P0 | 5 |
| FE-024 | Message bubbles | Incoming vs outgoing styling | Outgoing = green right; incoming = elevated left; show timestamp | FE-023 | P0 | 3 |
| FE-025 | Composer + send | POST message with idempotency | `client_message_id` UUID; Enter to send; Shift+Enter newline | FE-023 | P0 | 5 |
| FE-026 | Optimistic send | Pending → confirmed / rollback | Bubble shows pending state; duplicate retry does not duplicate UI | FE-025 | P1 | 5 |
| FE-027 | Chat header (live) | Peer name, avatar, Peer badge | Resolve peer from `user_a_id` / `user_b_id` vs current user | FE-021 | P1 | 3 |
| FE-028 | Empty states | No chats / no selection / no messages | Clear CTAs: “Start a chat”, “Select a conversation” | FE-021 | P2 | 2 |

**Epic exit:** Two users can chat via REST with correct bubble layout (realtime in E4).

---

### Epic E4: Realtime

| ID | Title | Description | Acceptance criteria | Deps | Priority | Points |
|----|-------|-------------|---------------------|------|----------|--------|
| FE-040 | WS ticket BFF | POST `/api/auth/ws-ticket` proxy | Frontend obtains ticket without exposing long-lived JWT in WS URL logs | FE-010 | P0 | 2 |
| FE-041 | WebSocket manager | Connect, ping/pong, reconnect | `lib/ws/manager.ts`; exponential backoff; status in UI store | FE-040 | P0 | 5 |
| FE-042 | Live message delivery | Handle `message.created` events | New messages append to active thread + update chat list preview | FE-041, FE-023 | P0 | 5 |
| FE-043 | Connection indicator | “Real-time connected” in chat window | Green dot when connected; yellow reconnecting; red offline | FE-041 | P1 | 2 |
| FE-044 | Gap recovery on reconnect | Fetch messages since last cursor | After reconnect, GET messages with `before`/`after` to fill gaps | FE-042 | P1 | 5 |

**Epic exit:** User A sends via REST → User B sees message without refresh.

---

### Epic E5: AI Context bar (Priority #1)

| ID | Title | Description | Acceptance criteria | Deps | Priority | Points |
|----|-------|-------------|---------------------|------|----------|--------|
| FE-050 | Context API integration | Fetch assistant context for conversation | GET scoped context; loading skeleton; error fallback | FE-023, **BE context API** | P0 | 5 |
| FE-051 | Context cards UI | Last met / Interested in / Follow-up | Three cards match mockup; empty values styled like “No summary yet” | FE-050 | P0 | 2 |
| FE-052 | Edit context mode | Inline edit fields + cancel | Edit toggles inputs; Cancel restores server state | FE-051 | P1 | 3 |
| FE-053 | Accept context | PATCH updated facts | Accept saves via API; toast on success/failure | FE-052, **BE PATCH context** | P1 | 3 |
| FE-054 | Context refresh | Poll or subscribe after new messages | Context updates after memory worker completes (poll 30s or WS event) | FE-050, FE-042 | P2 | 5 |

**Epic exit:** Context bar shows real AI-extracted facts; user can edit and accept.

---

### Epic E6: AI Copilot (Priority #2)

| ID | Title | Description | Acceptance criteria | Deps | Priority | Points |
|----|-------|-------------|---------------------|------|----------|--------|
| FE-060 | Copilot drawer UX | Open/close from header + `/copilot` route | Drawer slides in; backdrop click closes; focus trap | FE-002 | P0 | 2 |
| FE-061 | Copilot chat API | POST `/api/v1/copilot/chat` with conversation scope | Request includes `conversation_id`; response rendered in thread | FE-020, FE-023 | P0 | 5 |
| FE-062 | Quick action chips | Summarize, Find info, Suggest reply, Follow-up | Each chip pre-fills prompt and sends scoped request | FE-061 | P1 | 3 |
| FE-063 | Slash commands in composer | `/summarize`, `/suggest`, etc. | Parser detects `/` prefix; opens copilot or inline result | FE-025, FE-061 | P1 | 5 |
| FE-064 | Copilot message history | Persist thread in drawer session | Previous Q&A visible during session; clear on conversation switch | FE-061 | P2 | 3 |
| FE-065 | Insert suggestion to composer | “Use reply” copies AI text to composer | Does not auto-send; user confirms | FE-061, FE-025 | P1 | 2 |

**Epic exit:** User opens Copilot, asks scoped question, inserts suggested reply manually.

---

### Epic E7: AI Recommendations (Priority #3)

| ID | Title | Description | Acceptance criteria | Deps | Priority | Points |
|----|-------|-------------|---------------------|------|----------|--------|
| FE-070 | Recommendation fetch | Load recommendation for active conversation | Card shows summary or empty state copy | FE-027, **BE recommendations API** | P0 | 5 |
| FE-071 | Recommendation card UI | Yellow card + lightbulb icon | Matches mockup; accessible contrast on `--accent-ai` | FE-070 | P0 | 2 |
| FE-072 | Dismiss action | POST dismiss | Card hides or shows dismissed state; persists across reload | FE-070, **BE dismiss** | P1 | 2 |
| FE-073 | Send reminder | Orange CTA → composer draft | Inserts reminder text into composer; does not auto-send | FE-070, **BE copilot/share draft** | P1 | 3 |
| FE-074 | Recommendations page | `/recommendations` aggregate view | List all pending recommendations across conversations | FE-070 | P2 | 5 |

**Epic exit:** Recommendation card shows real AI suggestion; user can dismiss or draft reminder.

---

### Epic E8: Info panel & peer profile

| ID | Title | Description | Acceptance criteria | Deps | Priority | Points |
|----|-------|-------------|---------------------|------|----------|--------|
| FE-080 | Collapsible panel | Toggle from chat header | Desktop: width animates 0 ↔ 300px; tablet: drawer overlay | FE-002 | P0 | 2 |
| FE-081 | Peer profile section | Avatar, name, Peer badge | Data from conversation peer user | FE-027 | P1 | 2 |
| FE-082 | Quick actions | Message + Call placeholder | Message focuses composer; Call disabled with tooltip “Coming soon” | FE-080 | P1 | 1 |
| FE-083 | Accordion sections | Channel info, Media, Privacy | Expand/collapse; empty states for media | FE-080 | P2 | 2 |

**Epic exit:** Right panel collapses smoothly; Call button visible but disabled.

---

### Epic E9: Secondary nav screens

| ID | Title | Description | Acceptance criteria | Deps | Priority | Points |
|----|-------|-------------|---------------------|------|----------|--------|
| FE-090 | Global search page | `/search` | Search conversations/messages (scoped); results list | **BE search API** | P2 | 8 |
| FE-091 | AI Hub dashboard | `/ai-hub` | Summary cards: memories, follow-ups, insights count | Multiple AI APIs | P2 | 8 |
| FE-092 | Notifications inbox | `/notifications` | List from `/api/v1/notifications`; mark read | FE-020 | P2 | 5 |
| FE-093 | Settings page | `/settings` | Profile display, logout, notification prefs placeholder | FE-014 | P2 | 3 |

---

### Epic E10: Quality, a11y & polish

| ID | Title | Description | Acceptance criteria | Deps | Priority | Points |
|----|-------|-------------|---------------------|------|----------|--------|
| FE-100 | Loading skeletons | Chat list, messages, context bar | Skeleton placeholders during fetch | E3, E5 | P1 | 3 |
| FE-101 | Error boundaries + toasts | Global error handling | API failures show retry; no white screen | E3 | P1 | 3 |
| FE-102 | Keyboard a11y | Focus order, aria labels | Composer, drawer, panel toggles keyboard accessible | E2–E8 | P2 | 3 |
| FE-103 | E2E smoke test | Playwright: login → send message | CI-ready spec for critical path | E3, E4 | P2 | 5 |

---

## 7. Suggested implementation order

```
E1 Foundation (done scaffold)
  → E2 Auth
  → E3 Chat core
  → E4 Realtime
  → E5 Context bar      ★ AI #1
  → E6 Copilot          ★ AI #2
  → E7 Recommendations  ★ AI #3
  → E8 Info panel polish
  → E9 Secondary screens
  → E10 Quality
```

**MVP demo checkpoint (Chat + AI full):** Complete through **E7** with backend APIs for context, copilot, and recommendations.

---

## 8. Component → task matrix

| Component | File | Tasks |
|-----------|------|-------|
| `AppShell` | `components/layout/app-shell.tsx` | FE-002 |
| `NavSidebar` | `components/layout/nav-sidebar.tsx` | FE-002, FE-014, FE-015 |
| `ChatListPanel` | `components/layout/chat-list-panel.tsx` | FE-021, FE-022, FE-028 |
| `ChatWindow` | `components/layout/chat-window.tsx` | FE-023–027, FE-043 |
| `MessageBubble` | `components/chat/message-bubble.tsx` *(to create)* | FE-024, FE-026 |
| `Composer` | `components/chat/composer.tsx` *(to create)* | FE-025, FE-063, FE-065, FE-073 |
| `AIContextBar` | `components/ai/ai-context-bar.tsx` | FE-051–054 |
| `CopilotDrawer` | `components/ai/copilot-drawer.tsx` | FE-060–065 |
| `AIRecommendationCard` | `components/ai/ai-recommendation-card.tsx` | FE-071–073 |
| `InfoPanel` | `components/layout/info-panel.tsx` | FE-080–083 |
| `NewChatModal` | `components/chat/new-chat-modal.tsx` *(to create)* | FE-022 |
| `WebSocketManager` | `lib/ws/manager.ts` *(to create)* | FE-041–044 |

---

## 9. Definition of Done (project level)

- [ ] Two browser sessions (User A / User B) exchange messages in real time
- [ ] JWT never stored in `localStorage` / `sessionStorage`
- [ ] AI Context bar shows server data for active conversation
- [ ] Copilot answers scoped to active conversation only
- [ ] Recommendation card supports dismiss + draft reminder
- [ ] Info panel collapses on desktop; drawer on smaller viewports
- [ ] Call button visible, disabled, labeled “Coming soon”
- [ ] All user-facing strings in English
- [ ] `npm run build` passes with no TypeScript errors

---

## 10. Open questions (for your edits)

- [ ] User discovery for New Chat: search by **email**, **handle**, or both?
- [ ] Should Copilot stream responses (SSE) or single JSON response for MVP?
- [ ] Recommendation refresh: poll interval vs push notification?
- [ ] Mobile single-view navigation: include in MVP or defer?

---

## 11. Related docs

- Product spec: `docs/Specv2.md` (sections 51–56)
- Backend P2P contract: `rework.md`
- Frontend README: `frontend/README.md`
