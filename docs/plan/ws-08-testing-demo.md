# WS-08 — Testing & Demo

> **Mục tiêu:** Đảm bảo chất lượng MVP — Test tự động + Test thủ công + Demo Script + Video.

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | WS-08 (cuối cùng) |
| Độ phức tạp | 🟡 Trung bình |
| Phụ thuộc | Tất cả WS khác (WS-01 → WS-07) |
| Unblock | Không có (workstream cuối) |

---

## Trạng thái hiện tại

- ⬜ Test folder chưa có.
- ⬜ Demo script chưa viết.
- ⬜ Video demo chưa quay.
- ⬜ Slide chưa có.

---

## TASK-TEST-01: Backend tests (Repository + Service + API) ⬜

**Mục tiêu:** Test đầy đủ cho Backend — Repository + Service + API endpoints.

**Checklist:**
- [ ] Setup `pytest` + `pytest-asyncio` + `pytest-cov` + `httpx`
- [ ] Tạo `tests/conftest.py` với fixture: in-memory SQLite, test client, demo user
- [ ] Test `ConversationRepository` (CRUD + list_by_user)
- [ ] Test `MessageRepository` (CRUD + list_by_conversation)
- [ ] Test `ContactRepository` (CRUD + get_by_user)
- [ ] Test `MemoryRepository` (CRUD + get_by_contact)
- [ ] Test `EventLogRepository` (CRUD + list_recent)
- [ ] Test `RecommendationRepository` (CRUD + list_pending)
- [ ] Test `ContactService` (logic nghiệp vụ)
- [ ] Test `MessageService` (logic + emit event)
- [ ] Test `MemoryService` (logic + trigger agent — mock LLM)
- [ ] Test Auth Service (register, login, JWT)
- [ ] Test API Contact endpoints (FastAPI TestClient)
- [ ] Test API Conversation endpoints
- [ ] Test API Message endpoints
- [ ] Test API WebSocket (2 client giả lập)
- [ ] Test API Search endpoint
- [ ] Test API Recommendation endpoints
- [ ] Test API Copilot endpoint
- [ ] Test API Memory endpoint
- [ ] Coverage > 70% cho backend

**Commands:**
```bash
mkdir -p tests/{unit,api,e2e,ai}
touch tests/conftest.py
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## TASK-TEST-02: AI tests (Memory + Search + Recommendation + Copilot) ⬜

**Mục tiêu:** Test riêng cho các AI Agent — đánh giá chất lượng Memory, Search, Recommendation.

**Checklist:**
- [ ] Tạo `tests/ai/test_memory_agent.py` — test Memory Agent với 5 conversation mẫu (verify summary + entities)
- [ ] Tạo `tests/ai/test_search_agent.py` — test Search Agent với 5 query mẫu (precision > 80%)
- [ ] Tạo `tests/ai/test_recommendation_agent.py` — test Recommendation Agent với 5 user scenarios (verify type + reason)
- [ ] Tạo `tests/ai/test_copilot.py` — test Copilot với 5 câu hỏi mẫu (verify response hợp lệ)
- [ ] Tạo `tests/ai/test_tagging_agent.py` — test Tagging Agent với 5 Contact mẫu (verify tags phù hợp)
- [ ] Tạo `tests/ai/test_connection_agent.py` — test Connection Agent với 10 Contact mẫu
- [ ] Tạo `tests/ai/test_insight_agent.py` — test Insight Agent với 5 Contact mẫu
- [ ] Tạo `tests/ai/test_embedding.py` — test OpenAI Embedding (mock API)
- [ ] Tạo `tests/ai/test_vector_store.py` — test ChromaDB upsert + query (in-memory Chroma)
- [ ] Test Embedding pipeline: Memory → Chunk → Embed → Upsert → Query đúng context

**Commands:**
```bash
pytest tests/ai -v
```

---

## TASK-TEST-03: E2E tests (full flow) ⬜

**Mục tiêu:** End-to-End test toàn bộ flow chính.

**Checklist:**
- [ ] Tạo `tests/e2e/test_full_flow.py`
- [ ] E2E: Register → Login → Create Contact → Open Chat → Send 5 Messages
- [ ] E2E: Trigger Memory Refresh → Verify Memory trong DB
- [ ] E2E: Search → Get result (verify semantic match)
- [ ] E2E: Recommendation → Accept (verify status update)
- [ ] E2E: Copilot question "Người này là ai?" → Get response (verify context)
- [ ] E2E: Share to Conversation → Send (verify message draft)
- [ ] E2E: WebSocket realtime 2 client (gửi/nhận qua WS)
- [ ] E2E: Tag suggestion → User approve (verify tag persisted)
- [ ] E2E: Connection suggestion → User accept (verify pair persisted)

**Commands:**
```bash
pytest tests/e2e -v

# Verify toàn bộ flow
make seed
pytest tests/ -v --tb=short
```

---

## TASK-TEST-04: Demo Script + Slide + Video ⬜

**Mục tiêu:** Tạo material để pitch và demo cho ban giám khảo.

**Checklist:**
- [ ] Viết Demo Script (5 phút) — phân cảnh: Login → Add Contact → Chat → Memory xuất hiện → Search → Copilot hỏi → Recommendation → Đóng
- [ ] Tạo Slide Pitching (10-15 slides) theo template `summary.md`:
  - Slide 1: Tên dự án + tagline
  - Slide 2: Vấn đề
  - Slide 3: Giải pháp
  - Slide 4: Tech Stack
  - Slide 5: Architecture overview
  - Slide 6: Database schema (11 bảng)
  - Slide 7: AI Workflow
  - Slide 8: Backend API + WebSocket
  - Slide 9: Frontend screenshot
  - Slide 10: Use cases demo
  - Slide 11: Roadmap sau MVP
  - Slide 12: Team
  - Slide 13: Q&A
- [ ] Quay Video Demo (3 phút) — record màn hình chạy demo script
- [ ] Upload Video lên YouTube (unlisted) hoặc nộp BTC
- [ ] Test demo script chạy trơn tru (3 lần liên tiếp không lỗi)

**Commands:**
```bash
# Chạy demo script
cat demo_script.md

# Quay video (Windows + OBS Studio)
# 1. Mở app
# 2. Chạy demo script
# 3. Record 3 phút
```

---

## TASK-TEST-05: Seed data + User Manual ⬜

**Mục tiêu:** Seed data đầy đủ cho demo + User Manual PDF.

**Checklist:**
- [ ] Mở rộng `scripts/seed.py` (từ WS-07) — tạo đầy đủ:
  - 5 Contact với profile đa dạng (lập trình viên, giáo viên, bác sĩ, designer, marketing)
  - 10-20 conversation messages cho mỗi Contact
  - 5 ContactMemory đầy đủ (summary, timeline, company, skills, interests)
  - 5 Recommendation (đa dạng type: FOLLOWUP, REPLY, PRIORITY)
  - 3 Tag per Contact
  - 2-3 Insight per Contact
- [ ] Soạn User Manual (PDF) — hướng dẫn sử dụng từng tính năng
- [ ] Viết README.md tổng (overview + cách chạy + demo script link)

**Commands:**
```bash
make seed
# Verify
sqlite3 data/app.db "SELECT COUNT(*) FROM contact;"
sqlite3 data/app.db "SELECT COUNT(*) FROM contact_memory;"
sqlite3 data/app.db "SELECT COUNT(*) FROM recommendation;"
```

---

## Kết quả mong đợi sau WS-08

```
✅ make test pass 100%
✅ Coverage > 70% cho backend
✅ E2E test pass (full flow chính)
✅ AI test pass (5 Memory + 5 Search + 5 Recommendation + 5 Copilot)
✅ Demo Script hoàn chỉnh (5 phút)
✅ Slide Pitching (10-15 slides) sẵn sàng
✅ Video Demo 3 phút đăng YouTube / nộp BTC
✅ User Manual PDF sẵn sàng
✅ Seed data đầy đủ (5 Contact + Memory + Recommendation)
✅ Demo chạy trơn tru 3 lần liên tiếp không lỗi
```
