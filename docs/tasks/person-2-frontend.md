# Member 2 — Frontend

> **Phụ trách:** WS-06 (Frontend) toàn bộ — React + Vite + TypeScript + TailwindCSS + VinUni Red.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | Tuần 1 → Tuần 6 |
| Độ phức tạp | 🟡 Trung bình |
| Phụ thuộc | Member 1 (Backend API) + Member 3 (WebSocket) |
| Unblock | Demo Material |

---

## Trạng thái hiện tại

- ✅ Đã đọc spec + plan.
- ✅ Setup Node.js 20 + npm.
- 🟡 Đang vào tuần 2 — GATE 1.
- ⬜ `frontend/` folder chưa tạo.

---

## Tuần 1 (23/07 – 29/07) ✅

- [x] Đọc `docs/general overview/07_Frontend_Architecture_&_UX.md`
- [x] Đọc `docs/plan/ws-06-frontend.md`
- [x] Cài Node.js 20 LTS + npm
- [x] Setup VS Code extension: ES7 React Snippets, Tailwind IntelliSense
- [x] Tạo GitHub branch `feat/frontend-setup`
- [x] Test Vite dev server (`npm create vite@latest`)

---

## Tuần 2 (30/07 – 05/08) 🟡 — GATE 1

> **Mốc:** 05/08 demo Frontend chạy được trên browser.

### T2 (30/07)
- [ ] TASK-FE-01: Tạo `frontend/` folder, init Vite + React + TS
- [ ] TASK-FE-01: Verify `npm run dev` lên `http://localhost:5173`

### T3 (31/07)
- [ ] TASK-FE-01: Cài TailwindCSS + cấu hình
- [ ] TASK-FE-01: Setup VinUni Red color tokens (`tailwind.config.js`)

### T4 (01/08)
- [ ] TASK-FE-01: Setup ESLint + Prettier
- [ ] TASK-FE-01: Cài React Router v6 + Zustand

### T5 (02/08)
- [ ] TASK-FE-01: Setup Axios client + TanStack Query
- [ ] TASK-FE-01: Tạo folder structure (`src/api/`, `src/pages/`, `src/components/`)

### T6 (03/08)
- [ ] TASK-FE-02: `src/theme/colors.ts` (VinUni Red tokens)
- [ ] TASK-FE-02: `src/theme/typography.ts`
- [ ] TASK-FE-02: Component `<Button>` (Primary, Secondary, Ghost)

### CN (04/08) — optional
- [ ] TASK-FE-02: Component `<Input>`, `<Card>`, `<Avatar>`, `<Badge>`
- [ ] Help Member 1 test API từ Frontend

### T2 (05/08) 🚨 **GATE 1**
- [ ] **Demo trên browser:** Trang chủ hiển thị + VinUni Red render đúng
- [ ] Verify: `http://localhost:5173/` → thấy landing page mockup
- [ ] Cập nhật `timeline.md` tuần 2

---

## Tuần 3 (06/08 – 12/08) ⬜

### T2 (06/08)
- [ ] TASK-FE-03: Page `<Login>` (form + submit)
- [ ] TASK-FE-03: Page `<Register>` (form + submit)

### T3 (07/08)
- [ ] TASK-FE-03: Auth API integration (`src/api/auth.ts`)
- [ ] TASK-FE-03: Lưu JWT vào localStorage + Zustand

### T4 (08/08)
- [ ] TASK-FE-03: Axios interceptor (auto-attach Bearer token)
- [ ] TASK-FE-03: Protected route wrapper `<RequireAuth>`

### T5 (09/08)
- [ ] TASK-FE-04: Page `<Home>` (Conversation List mockup)
- [ ] TASK-FE-04: Page `<Chat>` (Message List + Input mockup)

### T6 (10/08)
- [ ] TASK-FE-04: Component `<ContextCard>` (mockup)
- [ ] TASK-FE-04: Component `<MessageBubble>` (user / contact / ai)

### CN (11/08) — optional
- [ ] TASK-FE-04: WebSocket client hook `useWebSocket`
- [ ] TASK-FE-04: Auto-reconnect on disconnect

### T2 (12/08) 🎯 **MVP**
- [ ] **Demo:** Login → Home → Chat UI render đúng (có thể chưa kết nối WS thật)
- [ ] Member 3 có API + WS sẵn sàng tích hợp
- [ ] Cập nhật `timeline.md` tuần 3

---

## Tuần 4 (13/08 – 19/08) ⬜

### T2 (13/08)
- [ ] TASK-FE-04: WebSocket integration (gửi/nhận Message thật)
- [ ] TASK-FE-04: Typing indicator + AI streaming response UI

### T3 (14/08)
- [ ] TASK-FE-04: Component `<MemoryTimeline>`
- [ ] TASK-FE-04: Component `<TagBadge>` + `<InsightList>`

### T4 (15/08)
- [ ] TASK-FE-04: Page `<ContactProfile>` (Memory + Timeline + Insight)

### T5 (16/08)
- [ ] TASK-FE-05: Page `<Search>` (search bar + result list + explanation)

### T6 (17/08)
- [ ] TASK-FE-05: Page `<RecommendationCenter>` (list + Accept/Reject)
- [ ] TASK-FE-05: Component `<RecommendationItem>`

### CN (18/08) — optional
- [ ] TASK-FE-05: Component `<AIReplySuggestion>` (Share to Conversation)

### T2 (19/08) 🚨 **GATE 2**
- [ ] **Demo:** Search → Copilot → Recommendation → Notification pages tất cả render được
- [ ] WebSocket chat realtime với 2 client
- [ ] VinUni Red primary color hiển thị đúng

---

## Tuần 5 (20/08 – 26/08) ⬜

### T2 (20/08)
- [ ] TASK-FE-05: Page `<Copilot>` (AI chat UI + streaming)
- [ ] TASK-FE-05: Page `<Notifications>` + `<Settings>`

### T3 (21/08)
- [ ] TASK-FE-05: Responsive mobile-first (test Chrome + Safari + Mobile view)
- [ ] TASK-FE-05: Polish UI (loading states, empty states, error states)

### T4 (22/08)
- [ ] Demo Script (5 phút) — phân cảnh: Login → Add Contact → Chat → Memory → Search → Copilot
- [ ] Test chạy Demo Script 3 lần

### T5 (23/08)
- [ ] Frontend manual test checklist (theo WS-08)
- [ ] Fix bug nếu phát hiện trong manual test

### T6 (24/08)
- [ ] TASK-FE-05: Build production (`npm run build`)
- [ ] Optimize bundle size + Lighthouse score > 80

### CN (25/08) — optional
- [ ] Final polish UI + animation

### T2 (26/08) — **Nộp hồ sơ Demo Day**
- [ ] Final commit `v1.0-mvp` tag
- [ ] Test build production serve qua backend

---

## Tuần 6 (27/08 – 01/09) ⬜

### T2 (27/08)
- [ ] Rehearsal lần 1 (toàn nhóm) — 5 phút demo
- [ ] Ghi nhận feedback

### T4 (29/08)
- [ ] Rehearsal lần 2 — target chạy trơn tru 5 phút

### T5 (30/08)
- [ ] Rehearsal lần 3 — target chạy trơn tru 5 phút

### T6 (31/08)
- [ ] Final rehearsal + Backup data
- [ ] Chuẩn bị: laptop + demo script in sẵn

### T2 (01/09) 🏆 **DEMO DAY**
- [ ] Setup trước 30 phút
- [ ] Demo 5 phút (chủ yếu thao tác trên Frontend)
- [ ] Q&A với BGK

---

## ✅ Checklist cuối cùng

```
Tất cả TASK-FE-* (5 tasks)          → STATUS
npm run dev                          → OK
npm run build                        → OK
WebSocket realtime                   → OK
Responsive mobile + desktop          → OK
VinUni Red primary color             → OK
Lighthouse score > 80                → OK
Demo Script (5 phút)                 → OK
```

---

## ⚠️ Vướng mắc

| Ngày | Vấn đề | Giải pháp |
|------|--------|-----------|
| (chưa có) | | |
