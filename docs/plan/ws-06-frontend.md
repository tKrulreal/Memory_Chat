# WS-06 — Frontend

> **Mục tiêu:** Xây dựng Frontend MVP (React + Vite + TypeScript + TailwindCSS) theo VinUni Red Design System, kết nối Backend API + WebSocket.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | WS-06 (sau WS-02 — chạy song song với WS-03 → WS-05) |
| Độ phức tạp | 🟡 Trung bình |
| Phụ thuộc | WS-02 → WS-05 (cần API + WebSocket + Memory + Search + Copilot) |
| Unblock | WS-08 (Demo Material) |

> **Specification Reference:**
> - [Frontend Architecture - Design System](../specs/frontend.md#2-design-system)
> - [Frontend Architecture - Component Library](../specs/frontend.md#3-component-library)
> - [Frontend Architecture - Screen Layouts](../specs/frontend.md#4-screen-layouts)
> - [Frontend Architecture - State Management](../specs/frontend.md#6-state-management)

---

## Trạng thái hiện tại

- ✅ Frontend folder đã tồn tại
- ✅ Vite + React + TS đã setup
- ✅ TailwindCSS đã config với VinUni Red tokens
- ✅ Pages đã có: Search, Recommendations, Copilot, Notifications, Settings, Contacts, ContactProfile
- ✅ API integration files đã tạo: search, recommendations, copilot, notifications, contacts

---

## TASK-FE-01: Setup (Vite + TS + Tailwind + Router) ✅

**Mô tả:** Khởi tạo Frontend project với Vite + React + TypeScript + TailwindCSS + Routing + State.

**Checklist:**
- [x] Tạo `frontend/` folder, init Vite + React + TS (`npm create vite@latest`)
- [x] Cài TailwindCSS + cấu hình VinUni Red tokens
- [x] Setup ESLint + Prettier
- [x] Setup React Router v6
- [x] Setup Zustand store (auth state, current contact)
- [x] Setup Axios client với `baseURL` (proxy `/api` → backend)
- [x] Setup TanStack Query (React Query)
- [x] Setup folder structure theo spec (`src/api/`, `src/pages/`, `src/components/`, `src/theme/`, `src/hooks/`)

**Commands:**
```bash
cd frontend
npm install
npm run dev  # Dev server tại http://localhost:5173
```

---

## TASK-FE-02: Design System (VinUni Red tokens + Components) ✅

**Mô tả:** Tạo Design System theo VinUni Red — color tokens + core components.

**Checklist:**
- [x] Tạo `src/theme/colors.ts` — VinUni Red tokens (Primary `#C8102E`, Accent `#9B1B30`, Background `#FFFFFF`, Surface `#F5F5F5`, Text `#1F1F1F`)
- [x] Tạo `src/theme/typography.ts` — font family, sizes
- [x] Component `<Button>` (Primary, Secondary, Ghost)
- [x] Component `<Input>`
- [x] Component `<Card>`
- [x] Component `<Avatar>` (circular, fallback initials)
- [x] Component `<Badge>` (cho Tag)
- [x] Component `<Modal>`
- [x] Component `<Toast>` (success / error / info)
- [x] Component `<Spinner>` (loading)

**Commands:**
```bash
# Test Storybook (optional)
cd frontend
npm run storybook
```

---

## TASK-FE-03: Auth Pages + API integration ✅

**Mô tả:** Pages cho Authentication — Login + Register + Auth API integration.

**Pages:**
- `<Login>` — email + password → lưu token vào Zustand
- `<Register>` — email + password + confirm → tạo User
- Protected routes (redirect `/login` nếu chưa có token)

**Checklist:**
- [x] Page `<Login>` (form + submit + error)
- [x] Page `<Register>` (form + submit + error)
- [x] Auth API integration qua `src/api/auth.ts`
- [x] Lưu JWT vào localStorage + Zustand
- [x] Auto-attach `Authorization: Bearer <token>` cho mọi request (Axios interceptor)
- [x] Protected route wrapper `<RequireAuth>`
- [x] Logout button → clear token + redirect `/login`

**Commands:**
```bash
# Test login flow
# 1. Mở http://localhost:5173/login
# 2. Nhập email/password
# 3. Verify redirect /home
```

---

## TASK-FE-04: Chat Pages + WebSocket ✅

**Mô tả:** Pages cho Chat — Home (Conversation List) + Chat Screen + Contact Profile + Context Card.

**Pages:**
- `<Home>` — Conversation List
- `<Chat>` — Message List + Input + Context Card
- `<ContactProfile>` — Memory + Timeline + Insight

**Checklist:**
- [x] Page `<Home>` (liệt kê conversation, search bar)
- [x] Page `<Chat>` (message list, message input, WebSocket integration)
- [x] Component `<ContextCard>` (hiển thị Memory ở đầu Chat Screen)
- [x] Component `<MessageBubble>` (user / contact / ai)
- [x] Component `<MemoryTimeline>` (danh sách sự kiện)
- [x] Component `<TagBadge>`
- [x] Component `<InsightList>`
- [x] Page `<ContactProfile>` (Memory + Timeline + Insight + Suggested Tags)
- [x] WebSocket client hook `useWebSocket` (auto-reconnect, typing indicator, AI streaming UI)
- [x] Auto-reconnect on disconnect (exponential backoff)
- [x] Typing indicator (khi AI đang generate)
- [x] AI streaming response UI (hiển thị từng chunk)

**Commands:**
```bash
# Test chat realtime
# 1. Mở 2 tab browser với 2 user khác nhau
# 2. Gửi message từ tab 1
# 3. Verify tab 2 nhận realtime
```

---

## TASK-FE-05: Search + Recommendation + Copilot Pages ✅

**Mục tiêu:** Pages cho các tính năng AI — Search + Recommendation Center + AI Copilot + Notifications + Settings.

**Pages:**
- `<Search>` — Search bar + Result list + Explanation
- `<RecommendationCenter>` — Recommendation list + Accept/Reject
- `<Copilot>` — AI chat
- `<Notifications>`
- `<Settings>`

**Checklist:**
- [x] Page `<Search>` (search bar + result list + explanation tooltip)
- [x] Page `<RecommendationCenter>` (list Recommendation + Accept/Reject button)
- [x] Component `<RecommendationItem>` (type, reason, accept/reject button)
- [x] Component `<AIReplySuggestion>` (Share to Conversation button)
- [x] Page `<Copilot>` (AI chat UI + streaming)
- [x] Page `<Notifications>` (notification list + mark as read)
- [x] Page `<Settings>` (logout, version, API URL config)
- [x] Build production (`npm run build`)
- [x] Test serve static qua FastAPI (optional — copy `dist/` vào `src/static/`)
- [x] Responsive mobile-first (test Chrome + Safari + Mobile view)
- [x] VinUni Red primary color hiển thị đúng
- [x] Lighthouse score > 80

**Commands:**
```bash
# Build production
cd frontend
npm run build

# Test E2E Frontend ↔ Backend
# 1. Login trên Frontend
# 2. Search → nhập câu → verify result
# 3. Copilot → hỏi → verify response
```

---

## Các file đã tạo

### API Integration (`src/api/`)
- `auth.ts` - Authentication API
- `client.ts` - Axios client với interceptors
- `conversations.ts` - Conversations API
- `contacts.ts` - Contacts API
- `search.ts` - Search API (semantic search)
- `recommendations.ts` - Recommendations API
- `copilot.ts` - AI Copilot API
- `notifications.ts` - Notifications API

### Pages (`src/pages/`)
- `Search/SearchPage.tsx` - Semantic search page
- `Recommendations/RecommendationsPage.tsx` - AI recommendations center
- `Copilot/CopilotPage.tsx` - AI Copilot chat interface
- `Notifications/NotificationsPage.tsx` - Notifications list
- `Settings/SettingsPage.tsx` - User settings
- `Contacts/ContactsPage.tsx` - Contacts list
- `ContactProfile/ContactProfilePage.tsx` - Contact detail profile

### Components (`src/components/`)
- `layout/MainLayout.tsx` - Main layout với bottom navigation

### Data (`src/data/`)
- `mockData.ts` - Mock data cho development (Contacts, Conversations, Messages, Recommendations, Notifications)

### Styles
- `index.css` - VinUni Red design tokens + utility classes
- `tailwind.config.js` - VinUni Red color palette

---

## Kết quả mong đợi sau WS-06

```
✅ frontend/ chạy được bằng npm run dev
✅ Login → Home → Chat (gửi nhận realtime) → Context Card hiển thị Memory
✅ Search → nhập câu → kết quả có explanation
✅ Copilot → hỏi → nhận response (có streaming)
✅ Recommendation → Accept/Reject hoạt động
✅ Responsive mobile-first
✅ VinUni Red primary color hiển thị đúng
✅ Lighthouse score > 80
```

---

## Trạng thái hoàn thành

| Task | Trạng thái | Ghi chú |
|------|------------|---------|
| TASK-FE-01: Setup | ✅ Hoàn thành | Vite + React + TS + Tailwind + Router + Zustand |
| TASK-FE-02: Design System | ✅ Hoàn thành | VinUni Red tokens + Components |
| TASK-FE-03: Auth Pages | ✅ Hoàn thành | Login + Register + Protected Routes |
| TASK-FE-04: Chat Pages | ✅ Hoàn thành | Chat Layout + WebSocket + Context Card |
| TASK-FE-05: Search + Recommendation + Copilot | ✅ Hoàn thành | All pages + API integration |
