# Timeline — MemoryChat MVP (6 tuần)

> **Mục tiêu:** Master timeline cho cả nhóm — biết tuần nào làm gì, ai làm gì, deadline nào.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | Tuần 1 → Tuần 6 |
| Độ phức tạp | 🟢 Thấp (tracking) |
| Phụ thuộc | `docs/plan/` |
| Unblock | Triển khai code |

---

## Trạng thái hiện tại (cập nhật 03/08/2026)

- ✅ Tuần 1 (23/07 – 29/07): Kick-off & Setup.
- ✅ Tuần 2 (30/07 – 02/08): **GATE 1** — Đã nộp 02/08 (Chủ nhật).
- 🟡 **Tuần 3 (03/08 – 09/08): MVP đầu tiên** — đang diễn ra.
- ⬜ Tuần 4 (10/08 – 16/08): GATE 2 — MVP hoàn chỉnh.
- ⬜ Tuần 5 (17/08 – 23/08): Nộp hồ sơ Demo Day.
- ⬜ Tuần 6 (24/08 – 01/09): Demo Day.

**Hôm nay:** 03/08/2026 (Thứ Hai) — Đầu tuần 3.

---

## Master Timeline (6 tuần)

```
Tuần 1 (23/07 - 29/07): Kick-off
  ▓▓▓▓▓▓▓▓ DONE ✅
  - Đọc spec, phân vai, setup Git
  - M1: Setup môi trường (Python 3.11, Docker, OpenAI key)
  - M2: Setup Node.js, Vite
  - M3: Setup Python env, test OpenAI API
  - M4: Setup Python env, test LangChain

Tuần 2 (30/07 - 02/08): GATE 1 — Chốt đề tài
  ▓▓▓▓▓▓▓▓ DONE ✅ (nộp 02/08 CN)
  - M1: Module 1 (DB Schema + Migration) + Module 2 (Repo+Service skeleton)
  - M2: Module 1 (Vite scaffold + Design System VinUni Red)
  - M3: Module 1 (Schemas + Contact API)
  - M4: Memory Agent prompt template + test 1 conversation mẫu
  - ALL: Demo GATE 1 — "Backend chạy + Frontend skeleton + Contact API"

Tuần 3 (03/08 - 09/08): MVP đầu tiên ⭐
  ▓░░░░░░░░ IN PROGRESS 🟡 (deadline 09/08)
  - M1: Module 3 (Auth + LLM Gateway) + Module 4 (API Skeleton + Tests)
  - M2: Module 2 (Auth pages + Chat pages + WebSocket client)
  - M3: Module 2 (Conversation/Message API + WS) + Module 3 (Embedding + Vector Store)
  - M4: Search Agent + Recommendation Agent
  - ALL: Demo MVP — "Chat + Memory + Search hoạt động"

Tuần 4 (10/08 - 16/08): GATE 2 — MVP hoàn chỉnh
  ░░░░░░░░░ TODO ⬜
  - M1: Module 5 (Dockerfile + Compose + Scripts + Health)
  - M2: Module 3 (Search + Rec + Copilot pages + polish)
  - M3: WS-03 hoàn thiện (Memory Agent + Worker + API) + Integration test
  - M4: Module 4 (Orchestrator + Copilot) + Module 5 (Tagging + Connection)
  - ALL: Demo GATE 2 — "Full MVP với Copilot hoạt động"

Tuần 5 (17/08 - 23/08): Nộp hồ sơ Demo Day
  ░░░░░░░░░ TODO ⬜
  - M1: Test suite backend + Slide (slides 1-5)
  - M2: Frontend polish + Demo script (5 phút)
  - M3: Seed data + Manual test checklist
  - M4: AI eval + Integration test + Video demo 3 phút
  - ALL: Nộp slide + video + user manual

Tuần 6 (24/08 - 01/09): Demo Day
  ░░░░░░░░░ TODO 🏆
  - 25/08 (T2): Rehearsal lần 1
  - 27/08 (T4): Rehearsal lần 2
  - 28/08 (T5): Rehearsal lần 3
  - 29/08 (T6): Final rehearsal + backup data
  - 01/09 (T2): DEMO DAY 5 PHÚT
```

---

## Critical Path

```
WS-01 (M1) ──┐
             ├──► GATE 1 (02/08) ✅ ──┐
WS-06-01 (M2)┘                       │
                                     ├──► MVP (09/08) ──┐
WS-02 (M3) ──────────────────────────┘                  │
                                                        ├──► GATE 2 (16/08) ──┐
WS-03 (M3) ─────────────────────────────────────────────┘                     │
                                                                           │
WS-04 (M4) ──────────────────────────────────────────────────────────────┤
                                                                           │
WS-05 (M4) ──────────────────────────────────────────────────────────────┤
                                                                           ├──► Demo (01/09)
WS-06 (M2) ─── chạy song song từ WS-02 ──────────────────────────────────┤
                                                                           │
WS-07 (M1) ─── chạy song song ─────────────────────────────────────────────┘
                                                                           │
WS-08 (ALL) ── chạy từ tuần 4 đến tuần 6 ─────────────────────────────────┘
```

**GATE đã qua:**
- ✅ **GATE 1 (02/08):** Backend + Frontend chạy được, demo "Hello → Login → Contact API" trên Swagger UI.

**GATE sắp tới:**
- **MVP (09/08):** Chat + Memory + Search hoạt động end-to-end.
- **GATE 2 (16/08):** MVP hoàn chỉnh với Copilot, Recommendation, Tagging.
- **Demo Day (01/09):** 5 phút demo chạy trơn tru trước BGK.

---

## Tuần 3 (03/08 – 09/08) — CHI TIẾT

> **Mốc quan trọng:** MVP đầu tiên vào 09/08 (Chủ Nhật).

### Member 1 — Backend + DevOps

- [ ] **T2 (03/08):** Module 3 — Auth (register/login API + JWT)
- [ ] **T3 (04/08):** Module 3 — LLM Gateway (retry + log + embed)
- [ ] **T4 (05/08):** Module 4 — API Skeleton (routers + middleware + CORS)
- [ ] **T5 (06/08):** Module 4 — Unit tests Repo + Service
- [ ] **T6 (07/08):** Module 4 — Tests Auth + Swagger docs polish
- [ ] **T7 (08/08):** Buffer / fix bug / help Member 3, 4
- [ ] **CN (09/08):** 🎯 **MVP** — Demo Backend có Auth + LLM + full Swagger

### Member 2 — Frontend

- [ ] **T2 (03/08):** Module 2 — Page `<Login>` + `<Register>` + Auth API integration
- [ ] **T3 (04/08):** Module 2 — Protected route + Axios interceptor
- [ ] **T4 (05/08):** Module 2 — Page `<Home>` + `<Chat>` mockup
- [ ] **T5 (06/08):** Module 2 — Components (ContextCard, MessageBubble)
- [ ] **T6 (07/08):** Module 2 — WebSocket client hook + auto-reconnect
- [ ] **T7 (08/08):** Polish UI + help Member 3 test WS
- [ ] **CN (09/08):** 🎯 **MVP** — Demo Frontend Login → Chat UI render đúng

### Member 3 — Chat + Memory

- [ ] **T2 (03/08):** Module 2 — Conversation API + Message API
- [ ] **T3 (04/08):** Module 2 — WebSocket endpoint + Connection Manager
- [ ] **T4 (05/08):** Module 2 — EventBus + dispatcher loop + EventLog
- [ ] **T5 (06/08):** Module 3 — EmbeddingService + VectorStoreService (ChromaDB)
- [ ] **T6 (07/08):** Module 3 — Memory Agent (summarize + extract entities)
- [ ] **T7 (08/08):** Integration test: gửi message qua WS → trigger Memory
- [ ] **CN (09/08):** 🎯 **MVP** — Demo Chat realtime + Memory auto-generated

### Member 4 — AI Copilot

- [ ] **T2 (03/08):** Module 1 — Search Agent (embed query + ChromaDB top-k)
- [ ] **T3 (04/08):** Module 1 — Search API + LLM re-rank
- [ ] **T4 (05/08):** Module 2 — Recommendation Agent (rule-based filter)
- [ ] **T5 (06/08):** Module 2 — Recommendation API (Accept/Reject)
- [ ] **T6 (07/08):** Module 2 — Insight Agent + API (3 loại Insight)
- [ ] **T7 (08/08):** Test Search Agent với 5 query mẫu (precision > 80%)
- [ ] **CN (09/08):** 🎯 **MVP** — Demo Search + Recommendation

---

## Weekly Checklist

Cập nhật cuối mỗi tuần:

### Tuần 1 (23/07 – 29/07) ✅
- [x] Đọc xong `docs/general overview/`
- [x] Đọc xong `docs/plan/`
- [x] Phân vai xong (xem README.md)
- [x] Setup Git repo + Slack channel
- [x] Setup môi trường cho 4 người
- [x] Test OpenAI API key hoạt động

### Tuần 2 (30/07 – 02/08) ✅
- [x] M1: Module 1 (DB Schema + Migration) + Module 2 (Repo+Service skeleton)
- [x] M2: Module 1 (Vite + Tailwind + VinUni Red tokens)
- [x] M3: Module 1 (Schemas + Contact API)
- [x] M4: Memory Agent prompt template + test 1 conversation mẫu
- [x] **GATE 1:** Nộp demo được "Hello World → Login → Contact API" — **02/08** ✅

### Tuần 3 (03/08 – 09/08) 🟡
- [ ] M1: Module 3 (Auth + LLM Gateway) + Module 4 (API Skeleton + Tests)
- [ ] M2: Module 2 (Auth + Chat pages + WebSocket client)
- [ ] M3: Module 2 (WS + EventBus) + Module 3 (Embedding + Vector Store + Memory Agent)
- [ ] M4: Module 1 (Search Agent) + Module 2 (Recommendation + Insight)
- [ ] **MVP:** Demo được "Chat + Memory + Search" — **09/08**

### Tuần 4 (10/08 – 16/08) ⬜
- [ ] M1: Module 5 (Dockerfile + Compose + Scripts + Health)
- [ ] M2: Module 3 (Search + Recommendation + Copilot pages)
- [ ] M3: Memory API + Worker + Integration test
- [ ] M4: Module 4 (Orchestrator + Copilot) + Module 5 (Tagging + Connection)
- [ ] **GATE 2:** Demo được Full MVP với Copilot — **16/08**

### Tuần 5 (17/08 – 23/08) ⬜
- [ ] M1: Test suite backend + Slide (slides 1-5)
- [ ] M2: Frontend polish + Demo script 5 phút
- [ ] M3: Seed data + Manual test checklist
- [ ] M4: AI eval + Integration test + Video demo 3 phút
- [ ] **Nộp hồ sơ:** Slide + Video + User Manual — **23/08**

### Tuần 6 (24/08 – 01/09) ⬜
- [ ] T2 (25/08): Rehearsal lần 1
- [ ] T4 (27/08): Rehearsal lần 2
- [ ] T5 (28/08): Rehearsal lần 3
- [ ] T6 (29/08): Final rehearsal + Backup data
- [ ] **T2 (01/09): 🏆 DEMO DAY**

---

## ⚠️ Vướng mắc & Blockers

| Tuần | Member | Vướng mắc | Status | Giải pháp |
|------|--------|-----------|--------|-----------|
| (chưa có) | | | | |

---

## Kết quả mong đợi sau 6 tuần

```
✅ MVP MemoryChat chạy được đầy đủ tính năng
✅ Backend (FastAPI + LangGraph + OpenAI + SQLite + ChromaDB)
✅ Frontend (React + Vite + VinUni Red)
✅ Demo script 5 phút + Video 3 phút + Slide + User Manual
✅ Source code tag v1.0-mvp
✅ Demo Day 01/09/2026 thành công 🏆
```