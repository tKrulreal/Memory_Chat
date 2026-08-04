# 09_AI_Agent_Architecture.md

# AI Agent Architecture

Project: MemoryChat

Version: MVP v1.0

---

# 1. Overview

MemoryChat không được xây dựng như một chatbot thông thường.

Hệ thống sử dụng kiến trúc Multi-Agent, trong đó mỗi Agent đảm nhiệm một nhiệm vụ chuyên biệt và phối hợp với nhau thông qua một Orchestrator trung tâm (LangGraph).

Kiến trúc này giúp:

- Tách biệt trách nhiệm giữa các Agent.
- Dễ mở rộng thêm Agent mới.
- Giảm Prompt Complexity.
- Dễ bảo trì.
- Có thể thay đổi LLM mà không ảnh hưởng Business Logic.

> **Trạng thái MVP hiện tại**: Codebase đã có `src/agents/graph.py` với một LangGraph `StateGraph` cơ bản gồm 2 node (`analyze`, `respond`). Các Agent chuyên biệt trong tài liệu này sẽ được xây dựng theo lộ trình trong [10_Roadmap_Development.md](10_Roadmap_Development.md).

---

# 2. AI Philosophy

AI trong MemoryChat không thay thế người dùng.

AI đóng vai trò là một trợ lý cá nhân (Personal Relationship Assistant).

Nguyên tắc thiết kế:

- AI hiểu ngữ cảnh.
- AI ghi nhớ dài hạn.
- AI đưa ra gợi ý.
- AI không tự động hành động.
- Người dùng luôn đưa ra quyết định cuối cùng.

---

# 3. High Level Architecture

```
                    User
                      │
               AI Copilot UI (sau MVP)
                      │
          Assistant Orchestrator (LangGraph)
                      │
        ┌─────────────┼─────────────┐
        │             │             │
 Intent Detection  Context Builder  Tool Registry
                      │
                AI Agent Layer
        ┌──────┬──────┬──────┬──────┐
        │      │      │      │      │
 Memory  Search  Tag   Recommendation
        │
 Connection
        │
 Insight
                      │
                 LLM Gateway
                      │
              OpenAI API (MVP)
```

---

# 4. Assistant Orchestrator

Assistant Orchestrator là "bộ não điều phối", hiện thực hoá bằng LangGraph `StateGraph`.

Nhiệm vụ:

- Phân tích yêu cầu người dùng.
- Chọn Agent phù hợp.
- Chọn Tool cần sử dụng.
- Xây dựng Context.
- Điều phối nhiều Agent.
- Tổng hợp kết quả.
- Trả Response cuối cùng.

Orchestrator không trực tiếp xử lý nghiệp vụ.

> **MVP**: `src/agents/graph.py` có một `StateGraph` với 2 node `analyze` → `respond`. Đây là skeleton sẽ mở rộng thành Orchestrator đầy đủ trong các sprint tiếp theo.

---

# 5. AI Context Builder

Đây là thành phần quan trọng trước khi gọi LLM.

Nó thu thập toàn bộ dữ liệu cần thiết:

- Recent Messages.
- Contact Memory.
- Timeline.
- User Profile.
- Contact Profile.
- Recommendation.
- Search History.
- Contact Insight.
- User Settings.

```
[All above]
  ↓
Context Object
  ↓
Prompt Builder
  ↓
LLM
```

Context Builder giúp:

- Giảm Token.
- Tránh thiếu ngữ cảnh.
- Chuẩn hoá đầu vào cho mọi Agent.

---

# 6. Prompt Builder

Prompt được tạo động.

```
System Prompt
  +
Agent Prompt
  +
Context
  +
Conversation
  +
User Query
  ↓
Final Prompt
```

Prompt của mỗi Agent được quản lý riêng trong Prompt Registry (sau MVP).

---

# 7. Tool Registry

Agent không truy cập trực tiếp Database. Mọi thao tác đều thông qua Tool.

Ví dụ:

- `search_contact()`
- `get_contact_memory()`
- `semantic_search()`
- `get_recent_messages()`
- `update_memory()`
- `generate_embedding()`
- `recommend_connection()`
- `get_relationship_score()`
- `get_contact_insight()`

Các Tool có thể được thay thế hoặc mở rộng mà không ảnh hưởng Agent.

---

# 8. LLM Gateway

LLM Gateway là lớp trung gian duy nhất giữa Agent và OpenAI.

Trong MVP, Gateway đã có tại `src/services/llm.py` (sử dụng `langchain_openai.ChatOpenAI`).

Vai trò:

- Khởi tạo `ChatOpenAI` từ `OPENAI_API_KEY` + `MODEL_NAME`.
- Retry khi lỗi (qua LangChain retry).
- Logging prompt và response.
- Tính token usage (sau MVP).

**Provider trong MVP**: OpenAI (`gpt-4o-mini`).

Provider dự kiến mở rộng sau MVP:

- Anthropic Claude.
- Google Gemini.
- Local LLM (Llama 3, Qwen, DeepSeek, Mistral) qua Ollama / vLLM.

Việc thêm provider chỉ cần đăng ký trong Gateway — không ảnh hưởng Agent.

---

# 9. Memory Agent

Vai trò: Biến hội thoại thành tri thức.

Input: Conversation.

Output:

- Summary.
- Timeline.
- Contact Memory.
- Relationship Score.

## Workflow

```
Conversation
  ↓
Chunk
  ↓
Summary
  ↓
Extract Entity
  ↓
Update Memory (SQLite)
  ↓
Embedding
  ↓
Upsert ChromaDB
  ↓
Done
```

Trigger:

- Conversation Idle.
- Refresh Memory.
- Batch Job.

---

# 10. Search Agent

Vai trò: Semantic Search.

Input: User Query.

## Workflow

```
User Query
  ↓
Embedding
  ↓
ChromaDB Similarity Search
  ↓
Retrieve
  ↓
Re-ranking
  ↓
LLM
  ↓
Answer
```

Ví dụ: *"Tìm người từng nói về AI Agent."*

---

# 11. Recommendation Agent

Đây là Agent quan trọng nhất.

Input:

- Contact Memory.
- User Behavior.
- Event Log.
- Contact Insight.

Output:

- Follow-up.
- Reply.
- Priority Contact.
- Merge Contact.
- Connection Recommendation.

## Workflow

```
Candidate Generation
  ↓
Rule Filter
  ↓
LLM Reasoning
  ↓
Ranking
  ↓
Recommendation
  ↓
Save (SQLite)
```

> Khi có Neo4j, Candidate Generation sẽ dùng Knowledge Graph để tăng chất lượng.

---

# 12. Tagging Agent

Nhiệm vụ: Trích xuất thông tin có cấu trúc.

Bao gồm:

- Company.
- Profession.
- Skill.
- Interest.
- Organization.
- Topic.
- Location.

Tag chỉ được đề xuất — người dùng xác nhận trước khi lưu.

---

# 13. Connection Agent

Agent chuyên phân tích quan hệ giữa các Contact.

Nguồn dữ liệu:

- Contact Memory.
- Embedding Similarity.
- Contact Insight.

Ví dụ: *"Hai Founder cùng tuyển AI Engineer."*

```
↓

Đề xuất kết nối.
```

AI không gửi lời giới thiệu thay người dùng.

---

# 14. Insight Agent

Insight Agent sinh ra các hiểu biết từ dữ liệu.

Ví dụ:

- Phản hồi nhanh vào buổi sáng.
- Quan tâm nhiều đến AI.
- Thường trao đổi về Startup.
- Có khả năng hợp tác.

Insight được lưu riêng để Recommendation tái sử dụng.

---

# 15. AI Copilot Agent

Agent tương tác trực tiếp với người dùng.

Copilot không tự xử lý. Nó chỉ:

- Hiểu Intent.
- Gọi Orchestrator.
- Trả kết quả.

Ví dụ: *"Người này là ai?"*

```
Memory Agent
  +
Insight Agent
  ↓
Merge
  ↓
Response
```

---

# 16. Agent Collaboration

Một yêu cầu có thể gọi nhiều Agent.

Ví dụ: *"Tôi nên nhắn gì cho người này?"*

```
Memory Agent
  ↓
Recommendation Agent
  ↓
Search Agent
  ↓
Merge Result
  ↓
Generate Response
  ↓
User
```

---

# 17. LangGraph Workflow

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

Mỗi Agent là một Node độc lập.

> MVP: `src/agents/graph.py` đã có `analyze` + `respond`. Các node mới sẽ được thêm theo Roadmap.

---

# 18. Human-in-the-Loop

Các Agent không được tự động:

- Gửi tin nhắn.
- Gắn Tag.
- Merge Contact.
- Kết nối hai người.
- Cập nhật Contact.

Mọi hành động đều cần xác nhận.

---

# 19. Memory Lifecycle

```
Message
  ↓
SQLite
  ↓
Event (EventLog)
  ↓
Memory Worker (asyncio task)
  ↓
Summary
  ↓
Embedding
  ↓
ChromaDB
  ↓
Recommendation
  ↓
Insight
  ↓
Done
```

> Sau MVP: Bổ sung cập nhật Neo4j để xây dựng Knowledge Graph quan hệ.

---

# 20. AI Security

Các bước kiểm tra (chi tiết hơn theo Roadmap):

- Prompt Injection Detection.
- Sensitive Data Detection.
- Context Isolation.
- Output Validation.
- PII Masking (future).

Mỗi User chỉ truy cập được Memory của chính mình.

---

# 21. Cost Optimization

- Không gọi LLM sau mỗi tin nhắn.
- Prompt Cache (in-memory MVP, Redis sau này).
- Context Compression.
- Batch Summary.
- Embedding Incremental.
- Reuse Contact Memory.
- Rule-based Filtering trước khi gọi LLM.
- Chọn model nhỏ (`gpt-4o-mini`).

---

# 22. MCP Ready Architecture

Kiến trúc được thiết kế để tương thích với Model Context Protocol (MCP).

Trong tương lai, Tool Registry có thể được thay thế bằng MCP Server mà không cần thay đổi Orchestrator.

Điều này cho phép AI kết nối với các dịch vụ bên ngoài như:

- Google Calendar.
- Gmail.
- Notion.
- Slack.
- CRM.
- GitHub.

---

# 23. AI Agent Design Principles

- Một Agent chỉ thực hiện một nhiệm vụ.
- Agent không truy cập trực tiếp Database.
- Tool là giao diện duy nhất để Agent lấy dữ liệu.
- Context được chuẩn hoá trước khi gọi LLM.
- AI luôn giải thích được lý do đưa ra gợi ý.
- Recommendation dựa trên nhiều nguồn dữ liệu, không chỉ LLM.
- Human-in-the-loop cho mọi hành động có ảnh hưởng đến người dùng.
- Toàn bộ kiến trúc hướng đến khả năng mở rộng và tích hợp thêm Agent trong tương lai.
- DB-agnostic: Agent làm việc qua Tool/Repository, không quan tâm backend lưu ở SQLite hay PostgreSQL, ChromaDB hay Qdrant.