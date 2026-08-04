# Tasks — MemoryChat (4 Members × 6 Weeks)

> **Mục tiêu:** Chia việc cho 4 người theo **module lớn** (gộp task nhỏ thành module), có tracking bằng checklist `[ ]` → `[x]`.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | Sau Plan (khi đã chốt WS) |
| Độ phức tạp | 🟢 Thấp (chỉ là tracking) |
| Phụ thuộc | `docs/plan/` |
| Unblock | Triển khai code |

---

## Timeline 6 tuần (cập nhật 03/08/2026)

| Tuần | Ngày | Mốc | Trạng thái |
|------|------|-----|------------|
| 1 | 23/07 – 29/07/2026 | Kick-off & Lập đội | ✅ DONE |
| 2 | 30/07 – 02/08/2026 | **GATE 1 — Chốt đề tài** | ✅ Nộp 02/08 |
| 3 | 03/08 – 09/08/2026 | **MVP đầu tiên** ⭐ | 🟡 IN PROGRESS |
| 4 | 10/08 – 16/08/2026 | **GATE 2 — MVP hoàn chỉnh** | ⬜ |
| 5 | 17/08 – 23/08/2026 | **Nộp hồ sơ Demo Day** | ⬜ |
| 6 | 24/08 – 01/09/2026 | **Demo Day** 🏆 | ⬜ |

**Hôm nay:** 03/08/2026 (Thứ Hai) — Đầu tuần 3, đang chuẩn bị MVP.

---

## Phân vai (4 người × 4 Modules)

| Member | Workstream | File | Phụ trách module |
|--------|------------|------|------------------|
| **Member 1** (Backend + DevOps) | WS-01 + WS-07 | [person-1-backend.md](./person-1-backend.md) | DB Schema, Repo+Service, Auth+LLM, Docker+Scripts |
| **Member 2** (Frontend) | WS-06 | [person-2-frontend.md](./person-2-frontend.md) | Setup+Design System, Auth+Chat, Search+Rec+Copilot |
| **Member 3** (Chat + Memory) | WS-02 + WS-03 | [person-3-chat-memory.md](./person-3-chat-memory.md) | Chat API, WebSocket+Bus, Memory+Embed+Vector |
| **Member 4** (AI Copilot) | WS-04 + WS-05 | [person-4-ai-copilot.md](./person-4-ai-copilot.md) | Search, Recommendation+Insight, Copilot Orchestrator |

**Quy ước gộp module:**
- Mỗi Module = gộp nhiều task nhỏ (TASK-XXX-NN) thành 1 đơn vị lớn.
- Checklist trong mỗi module liệt kê chi tiết cần làm.

---

## Trạng thái hiện tại

- ✅ Plan + Spec folder đã chuẩn hoá.
- ✅ Phân vai đã rõ.
- ✅ GATE 1 đã nộp ngày 02/08 (Chủ nhật).
- 🟡 **Đang vào tuần 3** — Target MVP ngày 09/08.
- ⬜ MVP demo chưa có.
- ⬜ Tuần 4 → 6 đang pending.

---

## Cách sử dụng

Mỗi Member đọc file của mình mỗi sáng:

1. Xem tuần hiện tại + module cần làm hôm nay.
2. Check `[ ]` thành `[x]` khi xong từng checklist con.
3. Cập nhật ghi chú nếu có vướng mắc.
4. Commit code + push lên git cuối ngày.

**Convention commit:**
```
feat(WS-01): db schema migration
feat(WS-02): contact API + WebSocket
docs(tasks): update week 3 progress
```

---

## File structure

```
docs/tasks/
├── README.md                  ← file này (overview)
├── timeline.md                ← master timeline + critical path
├── person-1-backend.md        ← Member 1 (Backend + DevOps) — 6 modules
├── person-2-frontend.md       ← Member 2 (Frontend) — 3 modules
├── person-3-chat-memory.md    ← Member 3 (Chat + Memory) — 3 modules
└── person-4-ai-copilot.md     ← Member 4 (AI) — 3 modules
```

---

## Quy tắc cập nhật

- Mỗi Member **bắt buộc** check `[ ]` → `[x]` ngay khi xong checklist con.
- Cuối tuần tổng kết: vào `timeline.md` cập nhật "Tuần X hoàn thành: Y/N".
- Nếu **Blocked** → ghi rõ trong section "⚠️ Vướng mắc" của file Member.

---

## Kết quả mong đợi

```
✅ 4 Member file chia theo module lớn (không quá nhỏ)
✅ Timeline master rõ ràng với critical path + tuần 2 đã hoàn thành
✅ Mỗi Member biết phải làm module gì trong tuần nào
✅ Cuối tuần 6 (01/09/2026): Demo thành công 5 phút
```