# Plan: Connection Recommendation System

## Context

**User Requirements:**
- Xây hệ thống gợi ý kết nối (Connection Recommendation)
- Mỗi user có profile
- Hệ thống tự đọc và gợi ý kết nối
- Frontend: Next.js/React
- Priority: Backend trước

**Theo spec (Section 32-33):**
- Không phải friend recommendation như Facebook
- Mục tiêu: phát hiện cơ hội kết nối có giá trị
- Ví dụ: User A cần AI Engineer, User B là AI Engineer đang tìm việc → gợi ý kết nối
- Luôn có Human-in-the-loop (PENDING → ACCEPTED/REJECTED)

**Current State:**
- Backend có: MemoryAgent, SearchAgent, RecommendationWorker (chỉ cho FOLLOWUP/REPLY)
- Đã có: Event system, Outbox pattern, ChromaDB, LLMGateway
- Thiếu: Contact model, ContactMemory model, ConnectionRecommendationAgent, Frontend UI

---

## Implementation Plan

### Phase 1: Data Models (Backend)

**1.1 Contact Model** - `src/models/contact.py`
```
Contact:
- id (UUID, PK)
- owner_user_id (FK → users)
- conversation_id (FK → conversations)
- display_name (string)
- email (string, nullable)
- phone (string, nullable)
- avatar_url (string, nullable)
- profession (string, nullable)
- company (string, nullable)
- notes (text, nullable)
- created_at, updated_at
```

**1.2 ContactMemory Model** - mở rộng Contact
```
ContactMemory:
- id (UUID, PK)
- contact_id (FK → contacts)
- summary (text)
- profession (string, nullable)
- company (string, nullable)
- skills (JSON array)
- interests (JSON array)
- location (string, nullable)
- relationship_score (int 0-100)
- last_interaction (datetime)
- updated_at
```

**1.3 Recommendation Model Update** - `src/models/ai.py`
Thêm relationship_id cho CONNECTION type:
```
Recommendation:
- id (UUID, PK)
- owner_user_id (FK → users)
- contact_id (FK → contacts, nullable) - cho FOLLOWUP/REPLY
- target_contact_id (FK → contacts, nullable) - cho CONNECTION
- type (enum: FOLLOWUP, REPLY, PRIORITY, CONNECTION)
- reason (text)
- priority (enum: HIGH, MEDIUM, LOW)
- confidence (float 0-1)
- status (enum: PENDING, ACCEPTED, REJECTED, DISMISSED)
- created_at, expires_at
```

### Phase 2: Backend Agents

**2.1 ConnectionRecommendationAgent** - `src/agents/connection/agent.py`
```python
class ConnectionRecommendationAgent:
    """
    Tìm kiếm cơ hội kết nối giữa các contacts của user.

    Logic:
    1. Lấy tất cả ContactMemory của user
    2. Phân tích mỗi contact về:
       - Đang tìm kiếm gì (needs)
       - Cung cấp gì (offers)
    3. Tìm cặp có complementary needs/offers
    4. Tính confidence score
    5. Generate recommendation
    """

    async def find_connections(
        self,
        user_id: uuid.UUID,
        limit: int = 5
    ) -> list[ConnectionRecommendation]
```

**2.2 ConnectionRecommendationWorker** - `src/workers/connection_worker.py`
```python
class ConnectionRecommendationWorker:
    """
    Subscribe: MEMORY_UPDATED, DAILY_CHECK
    Trigger: Khi có memory mới hoặc định kỳ
    """

    def subscribe(self):
        self._event_bus.subscribe(EventType.MEMORY_UPDATED, self._handle)

    async def _handle(self, event: ChatEvent):
        # Debounce để tránh spam
        # Gọi ConnectionRecommendationAgent
        # Lưu recommendation vào DB
        # Tạo notification cho user
```

**2.3 API Endpoints** - `src/api/v1/connections.py`
```
GET  /recommendations/connections        - Danh sách connection recommendations
POST /recommendations/connections/{id}/accept  - Chấp nhận kết nối
POST /recommendations/connections/{id}/reject   - Từ chối
GET  /recommendations/connections/{id}/details - Chi tiết (bao gồm cả 2 contact)
```

**2.4 Prompt Templates** - `src/agents/connection/prompts.py`
```python
# Phân tích contact để extract needs/offers
ANALYZE_NEEDS_PROMPT = """...
Phân tích contact và trả về:
- current_needs: Điều contact đang tìm kiếm
- current_offers: Điều contact có thể cung cấp
- match_keywords: Keywords để so khớp với contacts khác
"""

# So sánh 2 contacts
MATCH_ANALYSIS_PROMPT = """...
So sánh 2 contacts và đánh giá mức độ phù hợp để kết nối.
"""
```

### Phase 3: Frontend UI (Next.js)

**3.0 Existing Frontend Structure**
Dự án đã có Next.js frontend tại `frontend/` với:
- App Router (Next.js 15)
- TanStack Query (React Query v5)
- Zustand stores
- Tailwind CSS
- UI components tại `frontend/components/ui/`

**3.1 New Components** - `frontend/components/recommendations/`
```
recommendations/
├── ConnectionCard.tsx      # Card hiển thị 1 recommendation
├── ConnectionList.tsx     # Danh sách với tabs (Pending/Accepted/Rejected)
├── ConnectionDetail.tsx   # Modal/Page chi tiết
├── ConnectionSuggestModal.tsx  # Modal khi accept - gợi ý tin nhắn
└── index.ts               # Export tất cả
```

**3.2 Pages** - `frontend/app/(app)/recommendations/`
```
recommendations/
├── page.tsx               # Main recommendations page
└── [id]/
    └── page.tsx           # Connection detail page
```

**3.3 Hooks** - `frontend/hooks/`
```
useRecommendations.ts      # CRUD operations cho recommendations
useConnectionRecommendation.ts  # Specific hook cho connection type
```

**3.4 Types** - `frontend/types/`
```
recommendation.ts          # ConnectionRecommendation types
```

**3.5 API Service** - mở rộng `frontend/lib/api/`
```typescript
// recommendations.ts
export const getConnectionRecommendations = () => ...
export const acceptConnection = (id: string) => ...
export const rejectConnection = (id: string) => ...
export const getConnectionDetails = (id: string) => ...
```

**3.6 Zustand Store** - `frontend/lib/stores/`
```typescript
// recommendation-store.ts
interface RecommendationStore {
  connectionRecommendations: ConnectionRecommendation[];
  pendingCount: number;
  // actions...
}
```

**3.2 ConnectionCard Component**
```tsx
// Hiển thị một connection recommendation
interface ConnectionCardProps {
  recommendation: ConnectionRecommendation;
  onAccept: (id: string) => void;
  onReject: (id: string) => void;
  onViewDetails: (id: string) => void;
}
```

**3.3 ConnectionList Component**
```tsx
// Danh sách recommendations với filter
// Tab: Tất cả | Chờ xử lý | Đã chấp nhận | Đã từ chối
```

**3.4 ConnectionDetail Component**
```tsx
// Chi tiết kết nối
// - Thông tin contact A
// - Thông tin contact B
// - Lý do gợi ý
// - Nút Accept/Reject
// - Preview tin nhắn giới thiệu
```

**3.5 Recommendations Page**
```
/recommendations
├── Header với filter tabs
├── Stats summary (X connections suggested, Y accepted)
├── Connection recommendations list
└── Empty state nếu không có
```

### Phase 4: Integration

**4.1 Update RecommendationWorker**
- Thêm gọi ConnectionRecommendationAgent khi MEMORY_UPDATED

**4.2 Update main.py**
- Đăng ký ConnectionRecommendationWorker

**4.3 Update Event Types**
- Thêm CONNECTION_RECOMMENDATION_GENERATED event

---

## File Changes

### New Files (Backend)
```
src/models/contact.py              # Contact model
src/agents/connection/
├── __init__.py
├── agent.py                      # ConnectionRecommendationAgent
├── prompts.py                    # Prompt templates
├── schemas.py                    # Pydantic schemas
src/workers/connection_worker.py   # ConnectionRecommendationWorker
src/api/v1/connections.py         # API endpoints
```

### New Files (Frontend)
```
frontend/components/recommendations/
├── ConnectionCard.tsx
├── ConnectionList.tsx
├── ConnectionDetail.tsx
├── ConnectionSuggestModal.tsx
└── index.ts
frontend/app/(app)/recommendations/
├── page.tsx
└── [id]/page.tsx
frontend/hooks/useRecommendations.ts
frontend/lib/stores/recommendation-store.ts
frontend/types/recommendation.ts
```

### Modified Files
```
src/models/ai.py                  # Thêm target_contact_id vào Recommendation
src/schemas/enums.py              # Thêm CONNECTION type, DISMISSED status
src/workers/recommendation_worker.py  # Gọi ConnectionRecommendationAgent
src/main.py                       # Register worker
src/api/v1/notifications.py       # Thêm notification type
frontend/app/(app)/layout.tsx      # Thêm nav link đến recommendations
frontend/lib/api/index.ts         # Export thêm recommendation APIs
```

---

## Verification

1. **Backend Tests:**
   ```bash
   pytest tests/test_connection_agent.py
   pytest tests/test_connection_api.py
   ```

2. **Manual Testing:**
   - Tạo 2 contacts với complementary profiles
   - Trigger MEMORY_UPDATED event
   - Kiểm tra recommendation được tạo
   - Test API endpoints

3. **Frontend Testing:**
   - Chạy dev server: `cd frontend && npm run dev`
   - Navigate đến /recommendations
   - Test Accept/Reject buttons

---

## Priority Order (Backend First)

**Sprint 1 (Backend):**
1. Contact & ContactMemory models
2. ConnectionRecommendationAgent
3. API endpoints
4. ConnectionRecommendationWorker
5. Integration & Testing

**Sprint 2 (Frontend):**
1. Types & API services
2. Components (Card, List, Detail)
3. Recommendations page
4. Zustand store
5. Integration

---

## Estimated Effort

| Phase | Effort |
|-------|--------|
| Phase 1 (Models) | 2-3 giờ |
| Phase 2 (Backend Agents) | 4-6 giờ |
| Phase 3 (Frontend) | 3-5 giờ |
| Phase 4 (Integration) | 1-2 giờ |

**Total: ~10-16 giờ**
