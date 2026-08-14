# WS-08 — Testing & Demo

> **Mục tiêu:** Đảm bảo chất lượng MVP — Test tự động + Demo.

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

| Component | Status | Notes |
|-----------|--------|-------|
| Backend tests | ✅ Done | 158+ tests passing |
| AI Agent tests | ✅ Done | Memory, Search, Recommendation tests |
| API tests | ✅ Done | Auth, Chat, Contacts, etc. |
| Seed data | ✅ Done | Demo user + contacts |
| Demo Script | ⬜ Pending | Cần viết |
| Slide | ⬜ Pending | Cần tạo |
| Video Demo | ⬜ Pending | Cần quay |

---

## TASK-TEST-01: Backend Tests ✅

**Mô tả:** Unit tests cho Backend.

**Coverage:**

```
tests/
├── conftest.py          # Fixtures (DB, client, user)
├── test_auth.py        # Auth tests
├── test_api/
│   ├── test_auth.py
│   ├── test_contacts.py
│   ├── test_conversations.py
│   ├── test_messages.py
│   ├── test_memory.py
│   ├── test_search.py
│   └── test_recommendations.py
├── unit/
│   ├── repositories/
│   ├── services/
│   └── test_llm_gateway.py
└── test_websocket.py   # WebSocket tests
```

**Verify:**

```bash
pytest tests/ -v --cov=src
# Expected: 158+ tests pass
```

---

## TASK-TEST-02: AI Tests ✅

**Mô tả:** Tests cho AI Agents.

**Tests Created:**

- `tests/ai/test_memory_agent.py`
- `tests/ai/test_search_agent.py`
- `tests/ai/test_recommendation_agent.py`
- `tests/ai/test_copilot.py`
- `tests/ai/test_tagging_agent.py`
- `tests/ai/test_vector_store.py`

**Coverage:**

- Memory extraction quality
- Search precision
- Recommendation generation
- Copilot response validation

---

## TASK-TEST-03: E2E Tests ⬜

**Mô tả:** End-to-End tests toàn bộ flow.

**Flows to Test:**

```
1. Register → Login → Get token
2. Create Contact → Open Conversation → Send Messages
3. Trigger Memory Refresh → Verify Memory in DB
4. Search → Get results
5. Get Recommendations → Accept/Reject
6. Copilot question → Get response
7. WebSocket real-time message
```

**Status:** Cần hoàn thiện

---

## TASK-TEST-04: Demo Script + Slide + Video ⬜

**Mục tiêu:** Tạo material để demo.

**Demo Flow (5 phút):**

```
1. Giới thiệu sản phẩm (30s)
   - MemoryChat là gì
   - Tại sao cần AI Memory

2. Login + Tạo Contact (30s)
   - Demo user login
   - Search friend by phone
   - Send friend request

3. Chat + Memory (1 phút)
   - Send messages
   - Show auto-generated memory
   - Show Context Card

4. Semantic Search (30s)
   - Search "người làm AI"
   - Show results with explanation

5. AI Copilot (1 phút)
   - Ask "Người này là ai?"
   - Ask "Tôi nên reply thế nào?"
   - Show response

6. Recommendations (30s)
   - Show follow-up suggestions
   - Accept/Reject recommendation

7. Kết luận (30s)
   - Tóm tắt tính năng
   - Roadmap
```

**Slide Outline:**

```
1. Title: MemoryChat
2. Problem: Quá nhiều relationship, không nhớ nổi
3. Solution: AI-powered relationship memory
4. Tech Stack
5. Architecture
6. Demo Screenshots
7. AI Features: Memory, Search, Recommendation, Copilot
8. Roadmap
9. Team
10. Q&A
```

**Status:** Cần tạo

---

## TASK-TEST-05: Seed Data ⬜

**Mục tiêu:** Demo data đầy đủ.

**Seed Data Structure:**

```python
# Demo user
{
    "email": "demo@example.com",
    "password": "demo123",
    "full_name": "Demo User"
}

# 5 Contacts với đa dạng profiles:
[
    {"name": "Nguyễn Văn A", "profession": "Giáo viên", "company": "THPT XYZ"},
    {"name": "Trần Thị B", "profession": "AI Engineer", "company": "VinAI"},
    {"name": "Lê Văn C", "profession": "Bác sĩ", "company": "Bệnh viện ABC"},
    {"name": "Phạm Thị D", "profession": "Kế toán", "company": "Công ty DEF"},
    {"name": "Hoàng Văn E", "profession": "Kiến trúc sư", "company": "Công ty GHI"},
]

# Mỗi contact có:
# - 10-20 messages
# - ContactMemory (summary, skills, interests)
# - Tags (2-3 per contact)
# - Recommendations (1-2 per contact)
```

**Status:** Scripts đã có, cần verify data đầy đủ

---

## Verification Checklist

```
Backend:
  [ ] pytest pass 100%
  [ ] Coverage > 70%
  [ ] All migrations apply cleanly

API:
  [ ] /docs hiển thị đầy đủ endpoints
  [ ] Auth login/logout hoạt động
  [ ] CRUD operations hoạt động

AI:
  [ ] Memory Agent tạo memory đúng format
  [ ] Search Agent trả kết quả relevant
  [ ] Copilot trả response có context

Frontend:
  [ ] npm run dev chạy được
  [ ] Login → Chat flow hoạt động
  [ ] WebSocket realtime hoạt động

Demo:
  [ ] Demo script chạy trơn tru 3 lần liên tiếp
  [ ] Video quay được (3-5 phút)
  [ ] Slide sẵn sàng present
```

---

## Kết quả mong đợi sau WS-08

```
✅ pytest pass 100%
✅ Coverage > 70% cho backend
✅ E2E test pass (full flow chính)
✅ Demo Script hoàn chỉnh (5 phút)
✅ Slide Pitching sẵn sàng
✅ Video Demo 3-5 phút
✅ Seed data đầy đủ
✅ Demo chạy trơn tru 3 lần liên tiếp không lỗi
```

---

## Trạng thái hoàn thành

| Task | Status | Evidence |
|------|--------|----------|
| TASK-TEST-01: Backend Tests | ✅ Done | `tests/` (158+ tests) |
| TASK-TEST-02: AI Tests | ✅ Done | `tests/ai/` |
| TASK-TEST-03: E2E Tests | ⬜ In Progress | Cần hoàn thiện |
| TASK-TEST-04: Demo Script + Slide + Video | ⬜ Pending | Cần tạo |
| TASK-TEST-05: Seed Data | ✅ Done | `scripts/seed.py` |

---

## Reference

- [Testing Strategy](../specs/testing.md)
- [Demo Guidelines](../specs/demo.md)

---

*Version: 2.0 (Specv2 aligned)*
*Last Updated: 2026-08-14*
