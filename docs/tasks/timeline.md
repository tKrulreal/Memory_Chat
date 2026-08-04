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

## Trạng thái hiện tại

- ✅ Tuần 1: Kick-off & Setup (hoàn thành 23/07 – 29/07).
- 🟡 **Tuần 2: GATE 1 — Chốt đề tài** (đang diễn ra 30/07 – 05/08).
- ⬜ Tuần 3: MVP đầu tiên.
- ⬜ Tuần 4: GATE 2 — MVP hoàn chỉnh.
- ⬜ Tuần 5: Nộp hồ sơ Demo Day.
- ⬜ Tuần 6: Demo Day.

**Hôm nay:** Đầu tuần 2 (30/07/2026).

---

## Master Timeline (6 tuần)

```
Tuần 1 (23/07 - 29/07): Kick-off
  ▓▓▓▓▓▓▓▓ DONE
  - Đọc spec, phân vai, setup Git, setup Slack
  - M1: Setup môi trường (Python 3.11, Docker, OpenAI key)
  - M2: Setup Node.js, Vite
  - M3: Setup Python env, test OpenAI API
  - M4: Setup Python env, test LangChain

Tuần 2 (30/07 - 05/08): GATE 1 — Chốt đề tài
  ▓▓▓░░░░░ IN PROGRESS ⭐ DEADLINE 05/08
  - M1: WS-01 (Backend Foundation) — models + auth + LLM Gateway
  - M2: WS-06-01 (Vite scaffold) + WS-06-02 (Design System)
  - M3: WS-02 (Chat APIs) + WS-02 (WebSocket skeleton)
  - M4: Đọc spec Memory + Search, design prompt template
  - ALL: Demo GATE 1 — "Backend chạy + Frontend skeleton + Chat được"

Tuần 3 (06/08 - 12/08): MVP đầu tiên ⭐
  ░░░░░░░░░ TODO
  - M1: WS-01 hoàn thiện (Alembic, test)
  - M2: WS-06 (Auth pages + Chat pages + WebSocket client)
  - M3: WS-03 (Memory Agent + ChromaDB) ⭐ QUAN TRỌNG
  - M4: WS-04 (Search Agent + Recommendation Agent) ⭐ QUAN TRỌNG
  - ALL: Demo MVP — "Chat + Memory + Search hoạt động"

Tuần 4 (13/08 - 19/08): GATE 2 — MVP hoàn chỉnh
  ░░░░░░░░░ TODO
  - M1: WS-07 (Dockerfile + Makefile + backup)
  - M2: WS-06 (Search + Rec + Copilot pages + polish)
  - M3: WS-03 hoàn thiện + Integration test
  - M4: WS-05 (Orchestrator + Copilot + Tagging + Connection)
  - ALL: Demo GATE 2 — "Full MVP với Copilot hoạt động"

Tuần 5 (20/08 - 26/08): Nộp hồ sơ Demo Day
  ░░░░░░░░░ TODO
  - M1: WS-08 (test suite + CI) + Slide
  - M2: WS-08 (frontend test + responsive polish) + Demo script
  - M3: WS-08 (seed data + manual test)
  - M4: WS-08 (AI eval + integration test) + Video
  - ALL: Nộp slide + video + user manual

Tuần 6 (27/08 - 01/09): Demo Day
  ░░░░░░░░░ TODO 🏆
  - 27/08: Rehearsal lần 1
  - 29/08: Rehearsal lần 2
  - 30/08: Rehearsal lần 3
  - 31/08: Final rehearsal + backup data
  - 01/09: DEMO DAY 5 PHÚT
```

---

## Critical Path

```
WS-01 (M1) ──┐
             ├──► GATE 1 (05/08) ──┐
WS-06-01 (M2)┘                    │
                                  ├──► MVP (12/08) ──┐
WS-02 (M3) ──────────────────────┘                  │
                                                     ├──► GATE 2 (19/08) ──┐
WS-03 (M3) ──────────────────────────────────────────┘                     │
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

**GATE chính:**
- **GATE 1 (05/08):** Backend + Frontend chạy được, có thể demo "Hello World" → "Login" → "Chat" trên Swagger UI.
- **GATE 2 (19/08):** MVP hoàn chỉnh với Copilot, Recommendation, Tagging hoạt động → có thể demo cho stakeholder.
- **Demo Day (01/09):** 5 phút demo chạy trơn tru trước BGK.

---

## Tuần 2 (30/07 – 05/08) — CHI TIẾT

> **Mốc quan trọng:** GATE 1 — Chốt đề tài vào 05/08 (Thứ Ba).

### Member 1 — Backend + DevOps

- [ ] **T2 (30/07):** WS-01-T01 + T02 — Models User + Contact + Conversation + Message
- [ ] **T3 (31/07):** WS-01-T03 + T04 — ContactMemory + Recommendation + EventLog
- [ ] **T4 (01/08):** WS-01-T11 + T12 — Alembic init + migration đầu tiên
- [ ] **T5 (02/08):** WS-01-T13 + T14 — Repository skeleton + ConversationRepository
- [ ] **T6 (03/08):** WS-01-T15 + T16 — MessageRepository + ContactRepository
- [ ] **CN (04/08):** (optional) Buffer / fix bug
- [ ] **T2 (05/08):** 🚨 **GATE 1** — Demo Backend chạy được trên Swagger

### Member 2 — Frontend

- [ ] **T2 (30/07):** WS-06-T01 — Vite + React + TS scaffold
- [ ] **T3 (31/07):** WS-06-T02 — Tailwind + ESLint + Prettier
- [ ] **T4 (01/08):** WS-06-T04 + T05 — React Router + Zustand
- [ ] **T5 (02/08):** WS-06-T06 + T07 — Axios client + TanStack Query
- [ ] **T6 (03/08):** WS-06-T10 — VinUni Red color tokens
- [ ] **CN (04/08):** (optional) Buffer / fix bug
- [ ] **T2 (05/08):** 🚨 **GATE 1** — Demo Frontend chạy được trên browser

### Member 3 — Chat + Memory

- [ ] **T2 (30/07):** WS-02-T01 — Pydantic schemas cho Contact
- [ ] **T3 (31/07):** WS-02-T04 — API GET/POST /contacts
- [ ] **T4 (01/08):** WS-02-T05 — API GET/PUT/DELETE /contacts/{id}
- [ ] **T5 (02/08):** WS-02-T06 + T07 — Conversation API + List messages
- [ ] **T6 (03/08):** WS-02-T09 — WebSocket endpoint skeleton
- [ ] **CN (04/08):** (optional) Test WebSocket với 2 client
- [ ] **T2 (05/08):** 🚨 **GATE 1** — Demo Chat gửi/nhận qua WS

### Member 4 — AI Copilot

- [ ] **T2 (30/07):** Đọc `09_AI_Agent_Architecture.md` + design Memory prompt
- [ ] **T3 (31/07):** Đọc `06_AI_Workflow.md` + design Search prompt
- [ ] **T4 (01/08):** Setup `src/agents/memory/` package + prompt template
- [ ] **T5 (02/08):** Test Memory Agent với 1 conversation mẫu (verify LLM response)
- [ ] **T6 (03/08):** Test OpenAI Embeddings + ChromaDB upsert (local)
- [ ] **CN (04/08):** (optional) Design Recommendation rule engine
- [ ] **T2 (05/08):** 🚨 **GATE 1** — Demo "Memory Agent generate summary từ 5 messages"

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

### Tuần 2 (30/07 – 05/08) 🟡
- [ ] M1: 4 bảng models + migration chạy được
- [ ] M2: Vite + Tailwind + VinUni Red tokens render đúng
- [ ] M3: Contact/Conversation API + WebSocket skeleton
- [ ] M4: Memory Agent test với 1 conversation mẫu
- [ ] **GATE 1:** Demo được "Hello World" → "Login" → "Chat gửi/nhận"

### Tuần 3 (06/08 – 12/08) ⬜
- [ ] M1: WS-01 hoàn thiện (repositories + auth + LLM Gateway)
- [ ] M2: Auth pages + Chat UI + WebSocket client integration
- [ ] M3: WS-03 — Memory Agent + ChromaDB embed
- [ ] M4: WS-04 — Search Agent + Recommendation rule engine
- [ ] **MVP:** Demo được "Chat → Memory → Search"

### Tuần 4 (13/08 – 19/08) ⬜
- [ ] M1: WS-07 — Dockerfile + Makefile + backup script
- [ ] M2: Search + Recommendation + Copilot pages
- [ ] M3: WS-03 hoàn thiện + Integration test
- [ ] M4: WS-05 — Orchestrator + Copilot + Tagging + Connection
- [ ] **GATE 2:** Demo được Full MVP với Copilot

### Tuần 5 (20/08 – 26/08) ⬜
- [ ] M1: Test suite backend + Slide (slides 1-5)
- [ ] M2: Frontend polish + Demo script
- [ ] M3: Seed data + Manual test checklist
- [ ] M4: AI eval + Integration test + Video demo 3 phút
- [ ] **Nộp hồ sơ:** Slide + Video + User Manual

### Tuần 6 (27/08 – 01/09) ⬜
- [ ] T2 (27/08): Rehearsal lần 1 (full 5 phút, có feedback)
- [ ] T4 (29/08): Rehearsal lần 2 (target 5 phút không lỗi)
- [ ] T5 (30/08): Rehearsal lần 3 (target 5 phút không lỗi)
- [ ] T6 (31/08): Final rehearsal + Backup data + Kiểm tra slide
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