# WS-06 — Frontend

> **Mục tiêu:** Xây dựng Frontend MVP (React + Vite + TypeScript + TailwindCSS), kết nối Backend API + WebSocket.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | WS-06 (sau WS-05) |
| Độ phức tạp | 🟡 Trung bình |
| Phụ thuộc | WS-02 → WS-05 (API + WebSocket + Memory + Search + Copilot) |
| Unblock | WS-08 (Test + Demo) |
| Framework | React (Web App) |

---

## Trạng thái hiện tại

| Component | Status | File |
|-----------|--------|------|
| Setup (Vite + TS + Tailwind) | ✅ Done | `frontend/` |
| Design System (tokens + Components) | ✅ Done | `frontend/src/theme/` |
| Auth Pages (Login, Register) | ✅ Done | `frontend/src/pages/Auth/` |
| Chat Pages + WebSocket | ✅ Done | `frontend/src/pages/Chat/` |
| Contacts Page | ✅ Done | `frontend/src/pages/Contacts/` |
| Search + Recommendation Pages | ✅ Done | `frontend/src/pages/Search/`, `Recommendations/` |
| Copilot Page | ✅ Done | `frontend/src/pages/Copilot/` |
| Settings Page | ✅ Done | `frontend/src/pages/Settings/` |

---

## Frontend Architecture

### Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | React 18 + Vite |
| Language | TypeScript |
| Styling | TailwindCSS |
| State | Zustand |
| Data Fetching | TanStack Query |
| Routing | React Router v6 |
| HTTP Client | Axios |
| WebSocket | Native WebSocket API |

### Project Structure

```
frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Root component
│   ├── index.css              # Global styles
│   │
│   ├── api/                  # API client
│   │   ├── client.ts         # Axios instance
│   │   └── endpoints/        # API endpoints
│   │
│   ├── components/
│   │   ├── ui/              # Base UI components
│   │   │   ├── Button/
│   │   │   ├── Input/
│   │   │   ├── Card/
│   │   │   ├── Avatar/
│   │   │   ├── Tag/
│   │   │   ├── Spinner/
│   │   │   └── Modal/
│   │   ├── layout/           # Layout components
│   │   │   └── Layout.tsx
│   │   ├── chat/             # Chat components
│   │   │   ├── MessageBubble/
│   │   │   ├── ChatList/
│   │   │   ├── ContextCard/
│   │   │   └── ChatInput/
│   │   ├── contact/          # Contact components
│   │   └── ai/               # AI components
│   │       └── CopilotPanel/
│   │
│   ├── pages/
│   │   ├── Auth/
│   │   │   ├── Login/
│   │   │   └── Register/
│   │   ├── Chat/
│   │   │   ├── ChatListPage.tsx
│   │   │   └── ChatPage.tsx
│   │   ├── Contacts/
│   │   ├── Search/
│   │   ├── Recommendations/
│   │   ├── Copilot/
│   │   └── Settings/
│   │
│   ├── stores/               # Zustand stores
│   │   ├── authStore.ts
│   │   ├── chatStore.ts
│   │   ├── contactStore.ts
│   │   └── uiStore.ts
│   │
│   ├── hooks/                # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useChat.ts
│   │   ├── useWebSocket.ts
│   │   └── useAI.ts
│   │
│   ├── theme/                # Design tokens
│   │   ├── colors.ts
│   │   └── typography.ts
│   │
│   └── types/                # TypeScript types
│       └── index.ts
│
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── postcss.config.js
```

---

## TASK-FE-01: Setup ✅

**Mô tả:** Khởi tạo Frontend project.

**Files Created:**

- `package.json` — dependencies
- `tsconfig.json` — TypeScript config
- `vite.config.ts` — Vite config with proxy
- `tailwind.config.js` — Tailwind with custom tokens
- `postcss.config.js` — PostCSS config
- `index.html` — Entry HTML
- `public/favicon.svg`

**Dependencies:**

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.x",
  "zustand": "^4.x",
  "@tanstack/react-query": "^5.x",
  "axios": "^1.x",
  "tailwindcss": "^3.x",
  "typescript": "^5.x",
  "vite": "^5.x"
}
```

---

## TASK-FE-02: Design System ✅

**Mô tả:** Design tokens + base components.

**Theme Tokens:**

```typescript
// colors.ts
export const colors = {
  primary: "#EF4444",      // VinUni Red
  secondary: "#3B82F6",    // Blue
  accent: "#6E6E73",       // Gray
  
  surface: "#FFFFFF",
  background: "#F9FAFB",
  
  text: "#1F2937",
  textMuted: "#6B7280",
  
  success: "#10B981",
  warning: "#F59E0B",
  error: "#EF4444",
}

// typography.ts
export const typography = {
  fontDisplay: "Plus Jakarta Sans",
  fontBody: "DM Sans",
}
```

**Components Created:**

- `<Button>` — Primary, Secondary, Ghost, Danger variants
- `<Input>` — Text, Password, with icon support
- `<Card>` — Elevated, Flat, Pressed variants
- `<Avatar>` — Image, initials fallback, status indicator
- `<Tag>` — Removable, colored
- `<Spinner>` — Loading indicator
- `<Modal>` — Dialog overlay

---

## TASK-FE-03: Auth Pages ✅

**Mô tả:** Login + Register + Protected routes.

**Features:**

- Login form (email + password)
- Register form (full_name + email + password)
- JWT storage in localStorage
- Axios interceptor for auth header
- Protected route wrapper (`<RequireAuth>`)
- Logout clears token

---

## TASK-FE-04: Chat Pages ✅

**Mô tả:** Chat list + Chat screen + WebSocket integration.

**Pages:**

- `<ChatListPage>` — Conversation list with search
- `<ChatPage>` — Message list + Input + Context card

**Components:**

- `<MessageBubble>` — User, Contact, AI message styles
- `<ChatList>` — Conversation list with last message preview
- `<ContextCard>` — Shows contact memory at top
- `<ChatInput>` — Text input + send button + AI button
- `<CopilotPanel>` — AI Copilot bottom sheet

**WebSocket Features:**

- Connect on page load
- Auto-reconnect on disconnect (exponential backoff)
- Typing indicator
- Real-time message updates

---

## TASK-FE-05: Search + Recommendation + Copilot Pages ✅

**Mô tả:** AI features pages.

**Pages:**

- `<SearchPage>` — Search bar + results + explanation
- `<RecommendationsPage>` — List with Accept/Reject buttons
- `<CopilotPage>` — Standalone AI chat
- `<SettingsPage>` — User settings + logout
- `<ContactsPage>` — Contact list with memory preview

**API Integration:**

- TanStack Query for data fetching
- Optimistic updates for Accept/Reject
- Streaming for Copilot responses

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND COMPONENTS                         │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │    Auth    │  │    Chat     │  │  Contacts   │           │
│  │   Pages    │  │   Pages     │  │   Pages     │           │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘           │
│         │                │                │                   │
│         ▼                ▼                ▼                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │     UI      │  │     Chat    │  │     AI     │           │
│  │ Components  │  │ Components  │  │ Components  │           │
│  │ (Button,   │  │ (Message,  │  │ (Copilot,  │           │
│  │  Input,    │  │  ChatList, │  │  Search)   │           │
│  │  Card)     │  │  Context)  │  │             │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     STATE MANAGEMENT                      │   │
│  │          Zustand Stores (auth, chat, ui)               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     DATA LAYER                           │   │
│  │        TanStack Query + Axios + WebSocket               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Kết quả mong đợi sau WS-06

```
✅ frontend/ chạy được bằng npm run dev
✅ Login → Home → Chat (gửi nhận realtime) → Context Card hiển thị Memory
✅ Search → nhập câu → kết quả có explanation
✅ Copilot → hỏi → nhận response (có streaming UI)
✅ Recommendation → Accept/Reject hoạt động
✅ Responsive mobile-first
✅ Lighthouse score > 80
```

---

## Trạng thái hoàn thành

| Task | Status | Evidence |
|------|--------|----------|
| TASK-FE-01: Setup | ✅ Done | `frontend/package.json`, `vite.config.ts` |
| TASK-FE-02: Design System | ✅ Done | `frontend/src/theme/`, `components/ui/` |
| TASK-FE-03: Auth Pages | ✅ Done | `frontend/src/pages/Auth/` |
| TASK-FE-04: Chat Pages | ✅ Done | `frontend/src/pages/Chat/`, `components/chat/` |
| TASK-FE-05: Search + Recommendation + Copilot | ✅ Done | `frontend/src/pages/` |

---

## Reference

- [Frontend Architecture](../specs/frontend.md)

---

*Version: 2.0 (Specv2 aligned)*
*Last Updated: 2026-08-14*
