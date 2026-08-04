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

---

## Trạng thái hiện tại

- ⬜ Frontend folder chưa tồn tại.
- ⬜ Vite + React + TS chưa setup.
- ⬜ TailwindCSS chưa config VinUni Red tokens.
- ⬜ Pages chưa có.

**Lưu ý:** MVP chưa có Frontend — toàn bộ backend test qua Swagger UI. Frontend chỉ build khi API đã ổn định.

---

## TASK-FE-01: Setup (Vite + TS + Tailwind + Router) ⬜

**Mô tả:** Khởi tạo Frontend project với Vite + React + TypeScript + TailwindCSS + Routing + State.

**Checklist:**
- [ ] Tạo `frontend/` folder, init Vite + React + TS (`npm create vite@latest`)
- [ ] Cài TailwindCSS + cấu hình VinUni Red tokens
- [ ] Setup ESLint + Prettier
- [ ] Setup React Router v6
- [ ] Setup Zustand store (auth state, current contact)
- [ ] Setup Axios client với `baseURL` (proxy `/api` → backend)
- [ ] Setup TanStack Query (React Query)
- [ ] Setup folder structure theo spec (`src/api/`, `src/pages/`, `src/components/`, `src/theme/`, `src/hooks/`)

**Commands:**
```bash
cd frontend
npm install
npm run dev  # Dev server tại http://localhost:5173
```

---

## TASK-FE-02: Design System (VinUni Red tokens + Components) ⬜

**Mô tả:** Tạo Design System theo VinUni Red — color tokens + core components.

**Checklist:**
- [ ] Tạo `src/theme/colors.ts` — VinUni Red tokens (Primary `#C8102E`, Accent `#9B1B30`, Background `#FFFFFF`, Surface `#F5F5F5`, Text `#1F1F1F`)
- [ ] Tạo `src/theme/typography.ts` — font family, sizes
- [ ] Component `<Button>` (Primary, Secondary, Ghost)
- [ ] Component `<Input>`
- [ ] Component `<Card>`
- [ ] Component `<Avatar>` (circular, fallback initials)
- [ ] Component `<Badge>` (cho Tag)
- [ ] Component `<Modal>`
- [ ] Component `<Toast>` (success / error / info)
- [ ] Component `<Spinner>` (loading)

**Commands:**
```bash
# Test Storybook (optional)
cd frontend
npm run storybook
```

---

## TASK-FE-03: Auth Pages + API integration ⬜

**Mô tả:** Pages cho Authentication — Login + Register + Auth API integration.

**Pages:**
- `<Login>` — email + password → lưu token vào Zustand
- `<Register>` — email + password + confirm → tạo User
- Protected routes (redirect `/login` nếu chưa có token)

**Checklist:**
- [ ] Page `<Login>` (form + submit + error)
- [ ] Page `<Register>` (form + submit + error)
- [ ] Auth API integration qua `src/api/auth.ts`
- [ ] Lưu JWT vào localStorage + Zustand
- [ ] Auto-attach `Authorization: Bearer <token>` cho mọi request (Axios interceptor)
- [ ] Protected route wrapper `<RequireAuth>`
- [ ] Logout button → clear token + redirect `/login`

**Commands:**
```bash
# Test login flow
# 1. Mở http://localhost:5173/login
# 2. Nhập email/password
# 3. Verify redirect /home
```

---

## TASK-FE-04: Chat Pages + WebSocket ⬜

**Mô tả:** Pages cho Chat — Home (Conversation List) + Chat Screen + Contact Profile + Context Card.

**Pages:**
- `<Home>` — Conversation List
- `<Chat>` — Message List + Input + Context Card
- `<ContactProfile>` — Memory + Timeline + Insight

**Checklist:**
- [ ] Page `<Home>` (liệt kê conversation, search bar)
- [ ] Page `<Chat>` (message list, message input, WebSocket integration)
- [ ] Component `<ContextCard>` (hiển thị Memory ở đầu Chat Screen)
- [ ] Component `<MessageBubble>` (user / contact / ai)
- [ ] Component `<MemoryTimeline>` (danh sách sự kiện)
- [ ] Component `<TagBadge>`
- [ ] Component `<InsightList>`
- [ ] Page `<ContactProfile>` (Memory + Timeline + Insight + Suggested Tags)
- [ ] WebSocket client hook `useWebSocket` (auto-reconnect, typing indicator, AI streaming UI)
- [ ] Auto-reconnect on disconnect (exponential backoff)
- [ ] Typing indicator (khi AI đang generate)
- [ ] AI streaming response UI (hiển thị từng chunk)

**Commands:**
```bash
# Test chat realtime
# 1. Mở 2 tab browser với 2 user khác nhau
# 2. Gửi message từ tab 1
# 3. Verify tab 2 nhận realtime
```

---

## TASK-FE-05: Search + Recommendation + Copilot Pages ⬜

**Mục tiêu:** Pages cho các tính năng AI — Search + Recommendation Center + AI Copilot + Notifications + Settings.

**Pages:**
- `<Search>` — Search bar + Result list + Explanation
- `<RecommendationCenter>` — Recommendation list + Accept/Reject
- `<Copilot>` — AI chat
- `<Notifications>`
- `<Settings>`

**Checklist:**
- [ ] Page `<Search>` (search bar + result list + explanation tooltip)
- [ ] Page `<RecommendationCenter>` (list Recommendation + Accept/Reject button)
- [ ] Component `<RecommendationItem>` (type, reason, accept/reject button)
- [ ] Component `<AIReplySuggestion>` (Share to Conversation button)
- [ ] Page `<Copilot>` (AI chat UI + streaming)
- [ ] Page `<Notifications>` (notification list + mark as read)
- [ ] Page `<Settings>` (logout, version, API URL config)
- [ ] Build production (`npm run build`)
- [ ] Test serve static qua FastAPI (optional — copy `dist/` vào `src/static/`)
- [ ] Responsive mobile-first (test Chrome + Safari + Mobile view)
- [ ] VinUni Red primary color hiển thị đúng
- [ ] Lighthouse score > 80

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
