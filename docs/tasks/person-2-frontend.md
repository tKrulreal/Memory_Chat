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

## Module của Member 2 (3 modules)

| Module | Mô tả | Tuần |
|--------|-------|------|
| **M2-FE-01** | Setup + Design System (Vite + React + TS + Tailwind + VinUni Red) | Tuần 2 ✅ |
| **M2-FE-02** | Auth + Chat Pages (Login/Register + Home + Chat + WebSocket client) | Tuần 3 |
| **M2-FE-03** | Search + Recommendation + Copilot Pages (polish + Demo script) | Tuần 4 / Tuần 5 |

---

## Trạng thái hiện tại (cập nhật 03/08/2026)

- ✅ Đã đọc spec + plan.
- ✅ Setup Node.js 20 + npm.
- ✅ **GATE 1 đã nộp 02/08** (Chủ nhật tuần 2).
- ✅ M2-FE-01 (Vite scaffold + Design System VinUni Red) xong.
- 🟡 **Đang vào tuần 3** — M2-FE-02 (Auth + Chat Pages).
- ⬜ M2-FE-03 đang pending.

---

## Tuần 1 (23/07 – 29/07) ✅

- [x] Đọc `docs/general overview/07_Frontend_Architecture_&_UX.md`
- [x] Đọc `docs/plan/ws-06-frontend.md`
- [x] Cài Node.js 20 LTS + npm
- [x] Setup VS Code extension: ES7 React Snippets, Tailwind IntelliSense
- [x] Tạo GitHub branch `feat/frontend-setup`
- [x] Test Vite dev server (`npm create vite@latest`)

---

## Tuần 2 (30/07 – 02/08) ✅ — GATE 1

### Module M2-FE-01: Setup + Design System ✅

- [x] **Setup:** Tạo `frontend/` folder, init Vite + React + TS, verify `npm run dev`
- [x] TailwindCSS + ESLint + Prettier + VinUni Red color tokens (`tailwind.config.js`)
- [x] React Router v6 + Zustand + Axios client + TanStack Query
- [x] Folder structure: `src/api/`, `src/pages/`, `src/components/`, `src/theme/`
- [x] **Components:** `<Button>`, `<Input>`, `<Card>`, `<Avatar>`, `<Badge>`
- [x] Theme tokens: `src/theme/colors.ts` (VinUni Red), `typography.ts`

### 🚨 GATE 1 (02/08 CN) ✅
- [x] **Demo trên browser:** Landing page render đúng VinUni Red
- [x] Test gọi Contact API từ Frontend thành công
- [x] Nộp GATE 1 ngày **02/08 (Chủ nhật)**

---

## Tuần 3 (03/08 – 09/08) 🟡

### Module M2-FE-02: Auth + Chat Pages

- [x] **Auth API:** `src/api/auth.ts` — register + login + logout
- [x] Lưu JWT vào localStorage + Zustand store
- [x] **Page `<Login>`:** Form email/password + submit + error handling
- [x] **Page `<Register>`:** Form email/password/confirm + submit
- [x] **Axios interceptor:** auto-attach Bearer token + 401 → redirect Login
- [x] **Protected route wrapper `<RequireAuth>`**
- [x] **Page `<Home>`:** Conversation list (mockup hoặc gọi API)
- [x] **Page `<Chat>`:** Message list + input + typing indicator
- [x] **Components:** `<ContextCard>`, `<MessageBubble>` (user / contact / ai)
- [x] **Hook `useWebSocket`** — auto-reconnect on disconnect

### 🎯 MVP (09/08 CN)
- [ ] **Demo Frontend:** Login → Home → Chat UI render đúng + WebSocket gửi/nhận message
- [ ] Member 3 có API + WS sẵn sàng tích hợp
- [ ] Verify: 2 browser tab chat realtime thành công

---

## Tuần 4 (10/08 – 16/08) ⬜

### Module M2-FE-03 (phần 1): Search + Recommendation + Copilot Pages

- [ ] **Component `<MemoryTimeline>`** + `<TagBadge>` + `<InsightList>`
- [ ] **Page `<ContactProfile>`** (Memory + Timeline + Insight tabs)
- [ ] **Page `<Search>`** (search bar + result list + explanation card)
- [ ] **Page `<RecommendationCenter>`** (list + Accept/Reject buttons)
- [ ] **Component `<RecommendationItem>`** + `<AIReplySuggestion>`
- [ ] **Page `<Copilot>`** (AI chat UI + streaming response animation)
- [ ] **Page `<Notifications>`** + `<Settings>`

### 🚨 GATE 2 (16/08 CN)
- [ ] **Demo:** Search → Copilot → Recommendation → Notification pages tất cả render được
- [ ] VinUni Red primary color hiển thị đúng + responsive mobile/desktop
- [ ] Verify: Lighthouse score > 80

---

## Tuần 5 (17/08 – 23/08) ⬜

### Module M2-FE-03 (phần 2): Polish + Demo Material

- [ ] Responsive mobile-first (test Chrome + Safari + Mobile view)
- [ ] Polish UI (loading states, empty states, error states, animations)
- [ ] Build production (`npm run build`) + optimize bundle size
- [ ] **Demo Script (5 phút)** — phân cảnh:
  1. (30s) Login + Landing page giới thiệu MemoryChat
  2. (1m) Add Contact + mở Chat + nhắn 2-3 messages
  3. (1m) Xem ContactProfile → Memory Timeline + Insight
  4. (1m) Search "người thích lập trình Python" → top-5
  5. (1m) Copilot hỏi "Tôi nên nhắn gì với Nam?" → AI trả suggestion
  6. (30s) Recommendation Center → Accept 1 cái → Share to Conversation
- [ ] Test chạy Demo Script 3 lần + ghi nhận thời gian
- [ ] Final commit `v1.0-mvp` tag

---

## Tuần 6 (24/08 – 01/09) ⬜

- [ ] **T2 (25/08):** Rehearsal lần 1 (5 phút demo) — ghi nhận feedback
- [ ] **T4 (27/08):** Rehearsal lần 2 — target chạy trơn tru 5 phút
- [ ] **T5 (28/08):** Rehearsal lần 3 — target chạy trơn tru 5 phút
- [ ] **T6 (29/08):** Final rehearsal + backup build + chuẩn bị laptop
- [ ] **T2 (01/09) 🏆 DEMO DAY:** Demo 5 phút (chủ yếu thao tác trên Frontend) + Q&A

---

## ✅ Checklist cuối cùng (Tuần 6)

```
✅ M2-FE-01 → M2-FE-03 (3 modules)              → DONE
✅ npm run dev                                  → OK
✅ npm run build                                → OK
✅ WebSocket realtime                           → OK
✅ Responsive mobile + desktop                  → OK
✅ VinUni Red primary color                     → OK
✅ Lighthouse score > 80                        → OK
✅ Demo Script 5 phút (đã chạy 3 lần)          → OK
```

---

## ⚠️ Vướng mắc

| Ngày | Vấn đề | Giải pháp |
|------|--------|-----------|
| (chưa có) | | |