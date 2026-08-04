# 07_Frontend_Architecture_&_UX.md

# Frontend Architecture & User Experience

Project: MemoryChat

Version: MVP v1.0

---

# 1. Overview

Frontend của MemoryChat được thiết kế theo triết lý:

> Chat First, AI Native.

Điều này có nghĩa: Người dùng đến để nhắn tin. AI không chiếm toàn bộ giao diện. AI chỉ xuất hiện khi thực sự hữu ích.

Mục tiêu là tạo cảm giác AI luôn đồng hành nhưng không làm gián đoạn trải nghiệm nhắn tin.

> **Trạng thái MVP hiện tại**: Repository chưa có Frontend. MVP cung cấp **REST API** (`POST /api/v1/chat`, `GET /api/v1/status`). Frontend React / Flutter sẽ được xây dựng ở các sprint tiếp theo (xem [10_Roadmap_Development.md](10_Roadmap_Development.md)). Tài liệu này vẫn được giữ làm **Spec & Reference** cho team Frontend.

---

# 2. Design Principles

Toàn bộ UI được xây dựng theo 5 nguyên tắc.

## Invisible AI

AI luôn hoạt động phía sau. Người dùng không cần biết AI đang chạy.

Ví dụ:

- Mở chat → AI đã chuẩn bị Context.
- Tìm kiếm → AI hiểu semantic.
- Recommendation → AI tự sinh.

## Human First

AI không thay người dùng. Mọi hành động đều cần xác nhận.

Ví dụ:

```
Reply Suggestion
  ↓
Share to Conversation
  ↓
User Edit
  ↓
Send
```

## Context Aware

AI luôn biết:

- Conversation hiện tại.
- Contact hiện tại.
- Memory.
- Timeline.

Người dùng không cần nhập lại.

## Minimal Interaction

Một thao tác là đủ.

Ví dụ:

```
Click AI
  ↓
Result
```

Không cần qua nhiều bước.

## VinUni Red Identity

Sử dụng tông màu chủ đạo là VinUni Red.

Toàn bộ Brand, Button, Highlight đều dùng tông này.

---

# 3. UX Direction

Trải nghiệm tổng thể đi theo hướng **Message-centric AI**.

AI là lớp phụ trợi cho cuộc trò chuyện, không phải trung tâm của ứng dụng.

Các nguyên tắc UX:

- Không để AI chiếm quá 20% diện tích màn hình.
- Không tự động sinh nội dung gây giật mình.
- Cho phép người dùng tắt AI hoàn toàn.
- Cho phép chỉnh sửa Memory, Tag, Recommendation.

---

# 4. Recommended Tech Stack (sau MVP)

| Layer | Technology |
|-------|------------|
| Framework (Web) | ReactJS + TypeScript |
| Framework (Mobile) | Flutter |
| State Management | Zustand / Riverpod |
| Styling | TailwindCSS |
| Animation | Framer Motion / Rive |
| Realtime | WebSocket |
| API Client | TanStack Query / Axios |

Lý do:

- React: phổ biến, dễ tuyển người.
- Flutter: nếu cần Mobile đa nền tảng.
- TailwindCSS: design nhanh, dễ thống nhất Design System.

---

# 5. Recommended Folder Structure (sau MVP)

```
frontend/
├── src/
│   ├── app/
│   │   ├── main.tsx
│   │   └── router.tsx
│   ├── pages/
│   │   ├── Chat/
│   │   ├── Contact/
│   │   ├── Search/
│   │   ├── Recommendation/
│   │   └── Copilot/
│   ├── components/
│   ├── hooks/
│   ├── stores/
│   ├── services/      # API client
│   ├── theme/         # VinUni Red design system
│   └── utils/
└── package.json
```

---

# 6. Core Screens (sau MVP)

## Login / Register

- Email.
- Password.
- OAuth Google (sau này).

## Home

- Conversation List.
- Search bar.
- AI Suggestion Bar.

## Chat Screen

- Message list.
- Input box.
- AI Button.
- Context Card (mở rộng khi cần).

## Contact Profile

- Avatar.
- Company.
- Summary.
- Timeline.
- Skills.
- Interests.
- Relationship Score.

## Search Screen

- Search bar.
- Result list.
- Explanation từ AI.

## Recommendation Center

- Danh sách gợi ý.
- Accept / Reject.

## AI Copilot

- Input box.
- Streaming response.
- Share to Conversation.

## Context Card

- Mở khi vào Chat.
- Có thể đóng.

---

# 7. VinUni Red Design Tokens

```
Primary     : #A1232A
Secondary   : #1B1B1F
Surface     : #FFFFFF
Muted       : #6E6E73
Accent      : #FFD7DA
Background  : #FAFAFB
```

Typography:

- Sans-serif chính: Inter.
- Display: Inter Tight.

---

# 8. Navigation Pattern

- Bottom Navigation (mobile).
- Sidebar + Main (web).

Các tab chính:

- Chat.
- Contacts.
- Search.
- Recommendation.
- Copilot.

---

# 9. Realtime UX

Sử dụng WebSocket cho:

- Tin nhắn mới.
- Notification.
- AI Streaming Response.

UX:

- Typing indicator.
- Streaming text cho AI.
- Smooth animation khi có tin nhắn mới.

---

# 10. Accessibility

- Touch target >= 44px.
- Color contrast AA.
- Hỗ trợ screen reader.
- Keyboard navigation.

---

# 11. Performance UX

- Lazy load Conversation.
- Skeleton cho AI response.
- Tối ưu First Contentful Paint < 1.5s.

---

# 12. AI UX Principles

- AI luôn có giải thích.
- AI không spam notification.
- User có thể tắt AI.
- Mọi gợi ý có Accept / Reject.

---

# 13. Out of Scope (MVP)

Trong MVP chưa có:

- React/Flutter Frontend.
- Mobile build pipeline.
- CI/CD cho Frontend.
- Multi-region asset CDN.

Chỉ có Backend API.

Frontend sẽ được xây dựng ở các sprint tiếp theo.

---

# 14. Design Principles Summary

- Chat First.
- AI Native.
- Human-in-the-loop.
- Minimal Interaction.
- VinUni Red.
- Invisible AI.
- Context-aware.
- Privacy by Design.