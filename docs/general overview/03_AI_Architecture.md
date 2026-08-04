# 03_AI_Architecture.md

# AI Architecture

Project: MemoryChat

Version: MVP v1.0

---

# 1. Overview

MemoryChat được xây dựng theo kiến trúc AI-native.

Khác với ứng dụng chat truyền thống chỉ xem AI như một chatbot độc lập, trong MemoryChat, AI là thành phần cốt lõi của toàn bộ hệ thống.

Mọi dữ liệu sinh ra từ hội thoại đều được AI xử lý để tạo thành tri thức có cấu trúc (Structured Knowledge), phục vụ cho việc ghi nhớ, tìm kiếm và đưa ra recommendation.

Kiến trúc được thiết kế theo hướng modular nhằm đảm bảo mỗi AI Agent có trách nhiệm rõ ràng và có thể mở rộng độc lập trong tương lai.

---

# 2. AI Layer

Toàn bộ tầng AI bao gồm 6 thành phần chính.

```

```
                    AI Layer

                         │

                Assistant Orchestrator

                         │

        ┌────────┬────────┬────────┬────────┐

        │        │        │        │

 Memory Agent Search Agent Tagging Agent Recommendation Agent

                         │

                  AI Infrastructure

                         │

      PostgreSQL + Neo4j + Qdrant + Redis

```

Assistant Orchestrator đóng vai trò điều phối.

Bốn AI Agent chịu trách nhiệm xử lý nghiệp vụ.

AI Infrastructure cung cấp khả năng lưu trữ tri thức.

---

# 3. Assistant Orchestrator

Assistant Orchestrator là điểm vào duy nhất của toàn bộ hệ thống AI.

Nó không trực tiếp sinh câu trả lời.

Nhiệm vụ của Orchestrator là:

- Hiểu yêu cầu của người dùng.
- Xác định Intent.
- Quyết định Agent nào cần được gọi.
- Điều phối nhiều Agent nếu cần.
- Tổng hợp kết quả.
- Sinh câu trả lời cuối cùng.

Orchestrator được xây dựng bằng LangGraph nhằm hỗ trợ workflow nhiều bước và khả năng mở rộng sau này.

---

# 4. AI Copilot

AI Copilot là giao diện để người dùng tương tác với hệ thống AI.

AI Copilot không phải chatbot độc lập.

AI Copilot không phải AI Agent.

AI Copilot chỉ là lớp giao tiếp giữa người dùng và Assistant Orchestrator.

Trong mỗi cuộc trò chuyện sẽ có một nút **🤖 AI**.

Khi người dùng bấm vào, một bảng điều khiển (Bottom Sheet) sẽ xuất hiện.

Người dùng có thể:

- Xem tóm tắt cuộc trò chuyện.
- Xem hồ sơ liên hệ.
- Tìm kiếm thông tin.
- Hỏi AI bằng ngôn ngữ tự nhiên.
- Gợi ý trả lời.
- Gợi ý Follow-up.
- Gợi ý kết nối.
- Gợi ý Tag.

AI Copilot luôn hoạt động theo ngữ cảnh của Conversation hiện tại.

Do đó AI không cần hỏi:

"Bạn đang nói về ai?"

---

# 5. Tool Calling

Assistant Orchestrator sử dụng Tool Calling để quyết định Agent phù hợp.

Ví dụ

Người dùng hỏi:

"Người này làm ở đâu?"

↓

Intent Detection

↓

Memory Agent

↓

Contact Memory

↓

LLM

↓

Response

---

Người dùng hỏi:

"Tìm người làm AI ở Hà Nội."

↓

Search Agent

↓

Vector Search

↓

LLM

↓

Response

---

Người dùng hỏi:

"Có ai phù hợp để giới thiệu?"

↓

Recommendation Agent

↓

Neo4j

↓

Vector Search

↓

Ranking

↓

LLM

↓

Response

---

Nếu một câu hỏi cần nhiều nguồn dữ liệu.

Ví dụ:

"Người này là ai và mình nên trả lời thế nào?"

Assistant Orchestrator sẽ gọi:

Memory Agent

+

Recommendation Agent

Sau đó hợp nhất kết quả trước khi trả lời.

---

# 6. Memory Agent

Memory Agent chịu trách nhiệm chuyển đổi hội thoại thành tri thức lâu dài.

Input:

Conversation

Output:

Contact Memory

Timeline

Relationship Score

Summary

Memory Agent không được gọi sau mỗi tin nhắn.

Memory chỉ được cập nhật khi xảy ra Event phù hợp.

Ví dụ:

- Conversation Idle
- Conversation Closed
- 20 tin nhắn mới
- User yêu cầu cập nhật

Workflow

Conversation

↓

Chunking

↓

LLM Summary

↓

Memory Extraction

↓

Embedding

↓

Update Contact Memory

↓

Update Vector DB

↓

Update Knowledge Graph

---

# 7. Tagging Agent

Tagging Agent chịu trách nhiệm trích xuất các thực thể quan trọng từ hội thoại.

Bao gồm:

- Company
- Profession
- Skill
- Interest
- Topic
- Location
- Organization

Ví dụ

"Tôi đang làm AI Engineer tại VinAI."

↓

Company

VinAI

↓

Profession

AI Engineer

↓

Skill

AI

↓

Tag Recommendation

AI không tự động thêm Tag.

Người dùng phải xác nhận.

---

# 8. Search Agent

Search Agent chịu trách nhiệm Semantic Search.

Khác với tìm kiếm truyền thống dựa trên keyword.

Search Agent tìm theo ngữ nghĩa.

Ví dụ

"Tìm người từng hỏi về chatbot."

↓

Embedding Query

↓

Vector Search

↓

Top-k

↓

LLM Re-ranking

↓

Answer

Search Agent sử dụng:

- bge-m3
- Qdrant
- Gemini / GPT

---

# 9. Recommendation Agent

Recommendation Agent là thành phần quan trọng nhất của hệ thống.

Agent này không trả lời câu hỏi.

Nó chủ động tạo Recommendation dựa trên dữ liệu.

Recommendation bao gồm:

Follow-up Recommendation

Reply Recommendation

Tag Recommendation

Priority Contact

Merge Contact

Connection Recommendation

Recommendation dựa trên:

- Contact Memory
- Event History
- Relationship Score
- Knowledge Graph
- Semantic Similarity

---

# 10. AI Infrastructure

AI Infrastructure bao gồm bốn tầng lưu trữ.

### PostgreSQL

Lưu dữ liệu giao dịch.

- User
- Contact
- Conversation
- Message

---

### Qdrant

Lưu Embedding.

Bao gồm:

- Message
- Memory
- Summary

---

### Neo4j

Lưu Knowledge Graph.

Ví dụ

(User)-[:KNOW]->(Contact)

(Contact)-[:WORK_AT]->(Company)

(Contact)-[:INTEREST_IN]->(Topic)

---

### Redis

Lưu Cache.

Ví dụ:

Conversation Context

Recent Messages

LLM Cache

---

# 11. Context Management

Khi AI được gọi.

Context không chỉ bao gồm cuộc trò chuyện.

Mà còn bao gồm:

Conversation

+

Recent Messages

+

Contact Memory

+

Timeline

+

Recommendation History

+

Relationship Score

+

User Settings

Điều này giúp AI luôn hiểu đúng ngữ cảnh.

---

# 12. Human in the Loop

AI không được phép tự động:

- gửi tin nhắn
- thêm tag
- merge contact
- giới thiệu người
- sửa Contact Memory

Mọi hành động đều cần xác nhận.

Điều này giúp tăng độ tin cậy và bảo vệ quyền riêng tư.

---

# 13. Share to Conversation

Khi AI sinh nội dung.

Ví dụ:

Đề xuất trả lời.

Hoặc

Soạn Email.

Hoặc

Tóm tắt.

AI chỉ hiển thị kết quả.

Người dùng có hai lựa chọn.

Close

Hoặc

Share to Conversation

Nếu chọn Share.

Nội dung được đưa vào ô nhập tin nhắn.

Người dùng vẫn phải nhấn Send.

AI tuyệt đối không tự gửi tin.

---

# 14. Overall AI Workflow

                    User

                     │

               AI Copilot

                     │

         Assistant Orchestrator

                     │

      Intent Classification

                     │

     ┌────────┬────────┬────────┬────────┐

     │        │        │        │

 Memory Search Tagging Recommendation

     │        │        │        │

     └────────┴────────┴────────┘

               Context Builder

                     │

          PostgreSQL / Qdrant / Neo4j

                     │

                LLM Response

                     │

               AI Copilot UI

                     │

         Share to Conversation

                     │

             User Confirmation

                     │

               Send Message

---

# 15. Design Principles

- AI là trung tâm của hệ thống.
- Mỗi Agent chỉ đảm nhiệm một trách nhiệm.
- Copilot chỉ là giao diện, không phải Agent.
- Mọi Recommendation đều có thể giải thích.
- Human luôn là người ra quyết định cuối cùng.
- Hệ thống ưu tiên khả năng mở rộng và dễ bảo trì.
- Không thực hiện hành động tự động thay người dùng.