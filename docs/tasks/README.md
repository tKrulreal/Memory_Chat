# Tasks — MemoryChat (4 Members × 6 Weeks)

> **Mục tiêu:** Chia việc cho 4 người trong nhóm theo 6 tuần, có tracking tiến độ bằng checklist `[ ]` → `[x]`.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | Sau Plan (khi đã chốt WS) |
| Độ phức tạp | 🟢 Thấp (chỉ là tracking) |
| Phụ thuộc | `docs/plan/` |
| Unblock | Triển khai code |

---

## Timeline 6 tuần

| Tuần | Ngày | Mốc | Mục tiêu |
|------|------|-----|----------|
| 1 | 23/07 – 29/07/2026 | **Kick-off & Lập đội** | Setup môi trường, phân vai, đọc spec |
| 2 | 30/07 – 05/08/2026 | **GATE 1 — Chốt đề tài** | Backend skeleton + Frontend skeleton + Docker chạy được |
| 3 | 06/08 – 12/08/2026 | **MVP đầu tiên** ⭐ | Chat + Memory + Search hoạt động |
| 4 | 13/08 – 19/08/2026 | **GATE 2 — MVP** | Copilot + Recommendation + Integration |
| 5 | 20/08 – 26/08/2026 | **Nộp hồ sơ Demo Day** | Polish + Demo script + Video |
| 6 | 27/08 – 01/09/2026 | **Demo Day** 🏆 | Demo thật 5 phút + Slide + User Manual |

**Hôm nay:** Đầu tuần 2 (30/07/2026) — đang chuẩn bị vào **GATE 1**.

---

## Phân vai (4 người)

| Member | Workstream | File | Phụ trách |
|--------|------------|------|-----------|
| **Member 1** (Leader — Backend + DevOps) | WS-01 + WS-07 | [person-1-backend.md](./person-1-backend.md) | Models + Repositories + Auth + LLM Gateway + Docker + Makefile |
| **Member 2** (Frontend) | WS-06 | [person-2-frontend.md](./person-2-frontend.md) | React + Vite + Tailwind + Pages + WebSocket client |
| **Member 3** (Chat + Memory) | WS-02 + WS-03 | [person-3-chat-memory.md](./person-3-chat-memory.md) | Contact API + WebSocket + Event Bus + Memory Agent + ChromaDB |
| **Member 4** (AI Copilot) | WS-04 + WS-05 | [person-4-ai-copilot.md](./person-4-ai-copilot.md) | Search + Recommendation + Orchestrator + Copilot API + Tagging + Connection |

**WS-08 (Testing & Demo):** Tất cả 4 người cùng làm tuần 5 + 6.

---

## Trạng thái hiện tại

- ✅ Plan folder đã chuẩn hoá (`docs/plan/`).
- ✅ Spec folder đã chuẩn hoá (`docs/general overview/`).
- ✅ Phân vai đã rõ.
- ⬜ Tuần 1 đã hoàn thành (kick-off).
- 🟡 **Đang vào tuần 2** — GATE 1 ngày 05/08.
- ⬜ WS-01 chưa bắt đầu code.
- ⬜ WS-02 → WS-07 đang pending.

---

## Cách sử dụng

Mỗi Member đọc file của mình mỗi sáng:

1. Xem tuần hiện tại + checklist task cần làm hôm nay.
2. Check `[ ]` thành `[x]` khi xong.
3. Cập nhật ghi chú nếu có vướng mắc.
4. Commit code + push lên git cuối ngày.

**Convention commit:**
```
feat(WS-01): implement User model
fix(WS-02): WebSocket reconnect on disconnect
docs(tasks): update week 2 progress
```

---

## File structure

```
docs/tasks/
├── README.md                  ← file này (overview)
├── timeline.md                ← master timeline + critical path
├── person-1-backend.md        ← Member 1 (Backend + DevOps)
├── person-2-frontend.md       ← Member 2 (Frontend)
├── person-3-chat-memory.md    ← Member 3 (Chat + AI Memory)
└── person-4-ai-copilot.md     ← Member 4 (Search + Rec + Copilot)
```

---

## Quy tắc cập nhật

- Mỗi Member **bắt buộc** check `[ ]` → `[x]` ngay khi xong task (không để cuối tuần).
- Cuối tuần tổng kết: vào `timeline.md` cập nhật "Tuần X hoàn thành: Y/N".
- Nếu **Blocked** → ghi rõ trong section "⚠️ Vướng mắc" của file Member.

---

## Kết quả mong đợi

```
✅ 4 Member file có checklist cho 6 tuần
✅ Timeline master rõ ràng với critical path
✅ Mỗi Member biết phải làm gì trong tuần nào
✅ Cuối tuần 6 (01/09/2026): Demo thành công 5 phút
```