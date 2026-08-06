# Plan Overview & Tracking

> **Mục tiêu:** Bám sát tiến độ 8 Workstream, đảm bảo MVP MemoryChat demo được trong 6 tuần.

**Project:** MemoryChat
**Version:** MVP v1.0
**Template nền:** AI20K Agent Template (VinUni AI Thực Chiến)

---

## Tổng quan

| Thông tin | Chi tiết |
|-----------|----------|
| Thứ tự | Phase 0 (đầu tiên — setup plan) |
| Độ phức tạp | 🟢 Thấp |
| Phụ thuộc | Không có |
| Unblock | WS-01 → WS-08 |

**Trạng thái hiện tại:**

- ✅ Plan folder đã chuẩn hoá theo template.
- ✅ 8 Workstream files đã chuẩn hoá format.
- ✅ Dependency map đã rõ ràng.
- ⬜ Cập nhật tiến độ từng task sau khi bắt đầu code.

---

## 1. Mục tiêu tổng quát

MemoryChat = AI-native messaging platform có **long-term relationship memory**.

Trong MVP (6 tuần), nhóm cần chứng minh:

1. Chat hoạt động (REST + WebSocket realtime).
2. AI tự sinh **ContactMemory** từ hội thoại.
3. **Semantic Search** tìm lại Contact theo ngữ nghĩa.
4. **Recommendation** đề xuất Follow-up / Reply / Connection.
5. **AI Copilot** trả lời theo ngữ cảnh người dùng.
6. **Frontend** (React) chạy được end-to-end.

---

## 2. Workstream Map

| ID | Workstream | Status | Owner | Depends On |
|----|------------|--------|-------|------------|
| WS-01 | Backend Foundation | ✅ Done | Member 1 | — |
| WS-02 | Chat System | ⬜ Pending | Member 3 | WS-01 |
| WS-03 | AI Memory | ⬜ Pending | Member 1 + 4 | WS-01 + WS-02 |
| WS-04 | Search & Recommendation | ⬜ Pending | Member 4 | WS-03 |
| WS-05 | AI Copilot | ⬜ Pending | Member 4 | WS-03 + WS-04 |
| WS-06 | Frontend | ⬜ Pending | Member 2 | WS-02 → WS-05 |
| WS-07 | DevOps & Deployment | ⬜ Pending | Member 1 | — |
| WS-08 | Testing & Demo | ⬜ Pending | All | All |

**Status key:** 🟡 In Progress | ✅ Done | ⬜ Pending | 🔴 Blocked

---

## 3. Critical Path

```
WS-01 (Backend Foundation)
  ↓
WS-02 (Chat System)
  ↓
WS-03 (AI Memory)
  ↓
WS-04 (Search & Recommendation)
  ↓
WS-05 (AI Copilot)
  ↓
WS-08 (Testing & Demo)

WS-06 (Frontend) ─── chạy song song từ WS-02 đến WS-05
WS-07 (DevOps)      ─── chạy song song với tất cả
```

---

## 4. Mapping sang Sprint (tham khảo)

Mapping chỉ để tham khảo, không ràng buộc. Workstream là đơn vị tracking chính.

| Tuần | Workstream ưu tiên |
|------|---------------------|
| Week 1 | WS-01 + WS-07 |
| Week 2 | WS-02 + WS-06 (skeleton) |
| Week 3 | WS-03 |
| Week 4 | WS-04 + WS-06 (integration) |
| Week 5 | WS-05 + WS-06 (polish) |
| Week 6 | WS-08 (test + demo) |

---

## 5. Deliverables Tracking

| Hạng mục | File | Trạng thái |
|----------|------|------------|
| Spec | `docs/general overview/01-10` | ✅ |
| Plan | `docs/plan/00-ws-XX` | ✅ |
| Backend Skeleton | `src/` | ✅ (sẵn từ AI20K) |
| Database Schema | `src/models/` | ⬜ |
| Repository Layer | `src/repositories/` | ⬜ |
| Service Layer | `src/services/` | 🟡 (skeleton) |
| AI Agent | `src/agents/` | 🟡 (skeleton) |
| LLM Gateway | `src/services/llm.py` | ✅ |
| ChromaDB | `data/chroma/` | ⬜ |
| Frontend | `frontend/` | ⬜ |
| Docker | `docker-compose.yml` | ✅ |
| Demo Video | `demo/` | ⬜ |

---

## 6. Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM latency > 5s | Recommendation chậm | Chạy async qua EventBus, không block API |
| OpenAI API rate limit | Search fail | Retry + exponential backoff |
| Scope quá lớn | Không kịp demo | Ưu tiên P0, cắt P2 (Tagging/Connection) |
| Single container không scale | Khi nhiều user | Thiết kế DB-agnostic, sẵn sàng migrate PostgreSQL |
| ChromaDB persist corrupt | Mất embedding | Backup volume `./data/` bằng `make backup` |
| Prompt cost > budget | Hết tiền API | Dùng `gpt-4o-mini`, cache context |
| WebSocket không qua được proxy | Frontend không kết nối | Dùng sticky session hoặc poll fallback (optional) |

---

## 7. Definition of Done (toàn project)

- Tất cả 8 Workstream đạt "Done When".
- E2E test pass: Login → Chat → Memory → Search → Recommendation → Copilot.
- Demo chạy trơn tru trong 5 phút, 3 lần liên tiếp không lỗi.
- Tài liệu `docs/general overview` + `docs/plan` đầy đủ.
- Source code tag `v1.0-mvp`.

---

## 8. Cập nhật plan

Mỗi khi hoàn thành Task, cập nhật:

- ✅ Check vào Task ID trong file `ws-XX-*.md` (đổi `⬜` thành `[x]` trong checklist).
- ✅ Status Workstream trong bảng §2.
- ✅ Status Hạng mục trong bảng §5.

Trước khi commit lớn, cập nhật MemoryChat phiên bản nếu cần.

---

## Kết quả mong đợi sau Plan Setup

```
✅ Plan folder chuẩn hoá theo template format
✅ 8 Workstream files có task IDs nhất quán (TASK-BE/CHAT/MEM/SR/COP/FE/OPS/TEST)
✅ Dependency map rõ ràng
✅ Critical path xác định được
✅ Risk register đầy đủ
✅ Definition of Done thống nhất
```
