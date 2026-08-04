# 06_AI_Workflow.md

# AI Workflow

Project: MemoryChat

Version: MVP v1.0

---

# 1. Overview

MemoryChat không sử dụng AI như một chatbot độc lập.

AI được tích hợp xuyên suốt toàn bộ vòng đời của dữ liệu hội thoại.

Mỗi cuộc trò chuyện sau khi được tạo ra sẽ đi qua nhiều giai đoạn xử lý để dần chuyển đổi từ dữ liệu thô thành tri thức có cấu trúc.

Quy trình tổng quát:

```
Conversation
  ↓
Message Storage (SQLite)
  ↓
Event Generation
  ↓
Background Processing (asyncio task)
  ↓
Memory Extraction
  ↓
Knowledge Update (SQLite + ChromaDB)
  ↓
Recommendation
  ↓
AI Copilot
  ↓
User
```

Toàn bộ quá trình diễn ra bất đồng bộ nhằm đảm bảo trải nghiệm người dùng luôn mượt mà.

> Ghi chú: Toàn bộ tên database trong tài liệu này dùng cho MVP là **SQLite + ChromaDB**. Khi scale, các khối `Neo4j` / `Qdrant` sẽ được bổ sung theo [04_Database_Design.md](04_Database_Design.md) — không cần thay đổi workflow.

---

# 2. Event-Driven AI

Mọi hành động của người dùng đều tạo ra Event.

AI không theo dõi trực tiếp Database. Thay vào đó AI chỉ phản ứng với Event.

Ví dụ:

- `SEND_MESSAGE`
- `OPEN_CHAT`
- `OPEN_AI`
- `SEARCH`
- `UPDATE_CONTACT`
- `APPROVE_TAG`
- `REJECT_TAG`
- `SHARE_TO_CONVERSATION`
- `DELETE_MESSAGE`

Trong MVP:

- Mỗi Event được ghi vào bảng `EventLog` (SQLite).
- Một asyncio background task đọc Event mới và xử lý.

Sau MVP sẽ thay bằng Redis Stream / Kafka.

---

# 3. Workflow 1 — Memory Update

## Mục tiêu

Chuyển đổi lịch sử hội thoại thành Contact Memory.

## Trigger

Memory không được cập nhật sau mỗi tin nhắn.

Chỉ cập nhật khi:

- Conversation idle > 5 phút.
- Người dùng đóng cuộc trò chuyện.
- Có thêm 20 tin nhắn mới.
- Người dùng nhấn "Refresh AI Memory".
- Batch Job chạy ban đêm.

## Workflow

```
Conversation
  ↓
Load Recent Messages (SQLite)
  ↓
Chunking
  ↓
LLM Summary (OpenAI)
  ↓
Extract Entity
  ↓
Update ContactMemory (SQLite)
  ↓
Generate Embedding (OpenAI Embeddings)
  ↓
Upsert ChromaDB
  ↓
Save Event (SQLite)
```

## Output

- Summary.
- Timeline.
- Company.
- Profession.
- Skills.
- Interests.
- Relationship Score.
- Updated Memory.

> Trong tương lai sẽ thêm: Update Neo4j để xây dựng Knowledge Graph quan hệ.

---

# 4. Workflow 2 — Semantic Search

## Mục tiêu

Cho phép tìm kiếm bằng ngôn ngữ tự nhiên.

Ví dụ: *"Tìm người từng nói về Computer Vision."*

## Workflow

```
User Query
  ↓
Embedding Query (OpenAI Embeddings)
  ↓
ChromaDB Similarity Search (HNSW + Cosine)
  ↓
Top-k Result
  ↓
Retrieve Contact Memory (SQLite)
  ↓
LLM Re-ranking (OpenAI)
  ↓
Generate Answer
  ↓
Return Result
```

## Output

- Danh sách Contact phù hợp.
- Giải thích vì sao AI chọn các Contact này.

> Khi scale, ChromaDB sẽ được thay bằng Qdrant cluster.

---

# 5. Workflow 3 — Context Recall

## Trigger

Người dùng mở lại một cuộc trò chuyện.

## Workflow

```
Open Chat
  ↓
Load Contact Memory (SQLite)
  ↓
Load Last Discussion
  ↓
Load Timeline
  ↓
Load Recent Recommendation
  ↓
Generate Context Card
  ↓
Hiển thị:
  - Summary
  - Last Topic
  - Company
  - Skills
  - Relationship Score
  - Suggested Action
```

Context Card giúp người dùng nắm được toàn bộ bối cảnh mà không cần đọc lại lịch sử.

---

# 6. Workflow 4 — Recommendation

Recommendation không được sinh khi người dùng bấm nút. Recommendation được tạo chủ động ở Background.

## Trigger

- Memory Update.
- Event quan trọng.
- Batch Job.
- Người dùng tương tác nhiều với Contact.

## Workflow

```
Contact Memory (SQLite)
  +
Recent Events
  +
Relationship Score
  ↓
Recommendation Engine
  ↓
Rule-based Filtering
  ↓
LLM Reasoning (OpenAI)
  ↓
Recommendation Ranking
  ↓
Save Recommendation (SQLite)
  ↓
Notification
```

## Recommendation Types

- Follow-up Recommendation.
- Reply Suggestion.
- Tag Suggestion.
- Merge Contact.
- Priority Contact.
- Connection Recommendation.

> Khi có Neo4j, Recommendation sẽ dùng Knowledge Graph để candidate generation tốt hơn.

---

# 7. Workflow 5 — AI Copilot

AI Copilot là điểm tương tác chính giữa người dùng và AI.

Copilot không xử lý logic. Nó chỉ gửi yêu cầu tới Assistant Orchestrator (LangGraph).

## Workflow

```
User mở Copilot
  ↓
Assistant Orchestrator (LangGraph)
  ↓
Intent Detection
  ↓
Tool Selection
  ↓
Agent Selection
  ↓
Context Builder
  ↓
LLM (OpenAI)
  ↓
Generate Response
  ↓
Display Result
```

Copilot có thể gọi nhiều Agent trong cùng một yêu cầu.

Ví dụ: *"Người này là ai và mình nên trả lời thế nào?"*

```
Memory Agent
  +
Recommendation Agent
  ↓
Merge Result
  ↓
Response
```

Trong MVP, `src/agents/graph.py` đã có một LangGraph `StateGraph` với 2 node `analyze` + `respond`. Đây là skeleton cho Assistant Orchestrator sẽ phát triển.

---

# 8. Workflow 6 — Share to Conversation

Sau khi AI tạo ra:

- Suggested Reply.
- Draft Message.
- Summary.

Người dùng có thể chọn `Close` hoặc `Share to Conversation`.

## Workflow

```
AI Response
  ↓
User Click Share
  ↓
Copy to Input Box
  ↓
User Edit
  ↓
User Send
```

AI tuyệt đối không gửi tin nhắn thay người dùng.

---

# 9. Workflow 7 — Tagging

Tag được AI đề xuất chứ không tự động gắn.

## Workflow

```
Conversation
  ↓
Entity Extraction
  ↓
Generate Suggested Tags
  ↓
Hiển thị
  ↓
Approve
  ↓
Save Tag (SQLite)
```

Nếu người dùng từ chối:

```
Reject Event
  ↓
Learning Signal
```

Sau này hệ thống có thể dùng các sự kiện Approve/Reject để tinh chỉnh Recommendation.

---

# 10. Workflow 8 — Connection Recommendation

Mục tiêu: Đề xuất hai Contact nên được kết nối.

Ví dụ:

- Hai Founder cùng tuyển AI Engineer.
- Hai người cùng làm Computer Vision.
- Hai khách hàng có nhu cầu hợp tác.

## Workflow (MVP)

```
Contact Memory (SQLite)
  +
Embedding Similarity (ChromaDB)
  ↓
Candidate Generation
  ↓
Rule Filtering
  ↓
LLM Reasoning (OpenAI)
  ↓
Recommendation Score
  ↓
Present to User
  ↓
User Accept / Reject
```

AI không bao giờ tự giới thiệu hai người với nhau.

> Khi có Neo4j, Candidate Generation sẽ dùng Knowledge Graph để tăng chất lượng.

---

# 11. Workflow 9 — Contact Insight Generation

Ngoài Summary, AI còn sinh Insight.

Ví dụ:

- Quan tâm AI hơn Data Science.
- Phản hồi nhanh vào buổi sáng.
- Thường nhắc đến Startup.
- Đã nhiều lần hỏi về LLM.

## Workflow

```
Conversation
  ↓
Memory (SQLite)
  ↓
Behavior Analysis
  ↓
Insight Generation (OpenAI)
  ↓
Save Contact Insight (SQLite)
```

Insight sẽ được Recommendation Agent sử dụng.

---

# 12. AI Context Builder

Thay vì mỗi Agent tự truy vấn dữ liệu, Context Builder sẽ gom toàn bộ dữ liệu cần thiết.

Bao gồm:

- Recent Messages.
- Contact Memory.
- Timeline.
- Recommendation.
- User Settings.
- Contact Insight.
- Search History (nếu cần).

```
[All above]
  ↓
Context Object
  ↓
LLM
```

Việc chuẩn hoá Context giúp giảm Prompt Token và tăng chất lượng phản hồi.

---

# 13. Prompt Builder

Prompt không được hard-code. Prompt Builder sẽ tạo Prompt động.

```
System Prompt
  +
Context
  +
Memory
  +
User Query
  ↓
LLM Prompt
```

Điều này giúp dễ thay đổi Prompt theo từng Agent.

---

# 14. AI Response Validation

Trước khi trả kết quả cho người dùng, Response đi qua bước Validation.

Kiểm tra:

- Có rò rỉ dữ liệu người khác không.
- Có Prompt Injection không.
- Có thông tin nhạy cảm không.
- Có vượt phạm vi Context không.

Nếu thất bại, AI yêu cầu tạo lại Response.

Trong MVP, validation ở mức tối thiểu. Sau MVP sẽ thêm rule engine chuyên dụng.

---

# 15. Workflow Orchestration

Toàn bộ Workflow được quản lý bằng LangGraph.

```
START
  ↓
Intent Detection
  ↓
Planning
  ↓
Context Builder
  ↓
Select Agent
  ↓
Execute Agent
  ↓
Validate Output
  ↓
Merge Response
  ↓
END
```

Mỗi Node chỉ thực hiện một nhiệm vụ duy nhất — dễ mở rộng và dễ debug.

MVP hiện tại đã có một `StateGraph` cơ bản tại `src/agents/graph.py`. Orchestration đầy đủ sẽ được thêm vào các sprint tiếp theo.

---

# 16. Cost Optimization Strategy

Để giảm chi phí LLM, hệ thống áp dụng:

- Không gọi LLM sau mỗi tin nhắn.
- Cache Context (in-memory MVP, Redis sau này).
- Chỉ tạo Embedding khi cần.
- Summary theo Batch.
- Recommendation chạy nền.
- Reuse Contact Memory thay vì đọc lại toàn bộ Conversation.
- Chọn model nhỏ (`gpt-4o-mini`) cho tác vụ không cần lý luận sâu.

---

# 17. AI Workflow Principles

- Event-driven.
- Human-in-the-loop.
- Context-aware.
- AI First.
- Async Processing.
- Modular Agent.
- Explainable Recommendation.
- Privacy by Design.
- Cost-efficient.
- Scalable.
- DB-agnostic: workflow không phụ thuộc vào SQLite/ChromaDB/PostgreSQL/Qdrant — chỉ phụ thuộc Repository.