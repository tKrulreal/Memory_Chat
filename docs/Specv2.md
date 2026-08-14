# MemoryChat

## System Specification

**Version:** 1.0
**Status:** Draft for MVP
**Development Duration:** 6 weeks
**Program:** AI Thực chiến VinUni

---

# 1. Project Overview

## 1.1. Product

MemoryChat là một ứng dụng nhắn tin tích hợp AI Agent, tập trung vào việc giúp người dùng quản lý và khai thác thông tin từ các mối quan hệ thông qua lịch sử hội thoại.

Chat không phải giá trị cốt lõi của sản phẩm.

Chat đóng vai trò là nguồn dữ liệu để hệ thống AI:

* hiểu ngữ cảnh;
* xây dựng memory;
* quản lý contact;
* tìm kiếm thông tin;
* phát hiện cơ hội follow-up;
* đề xuất kết nối;
* hỗ trợ người dùng ngay trong cuộc hội thoại.

Product positioning:

> **AI-native Messaging Platform with Long-term Relationship Memory**

AI được định vị như một "Second Brain" cho người dùng.

---

# 2. Product Philosophy

MemoryChat không cố gắng trở thành một phiên bản khác của Messenger hoặc Zalo.

Giá trị cốt lõi nằm ở AI Layer.

Hệ thống phải có khả năng biến:

```text
Raw Conversation
        ↓
Structured Information
        ↓
Memory
        ↓
Knowledge
        ↓
Recommendation
        ↓
User Action
```

AI chỉ:

* hiểu;
* ghi nhớ;
* phân tích;
* tìm kiếm;
* đề xuất.

AI không tự động:

* gửi tin nhắn;
* kết bạn;
* giới thiệu người này với người khác;
* merge contact;
* thực hiện hành động có tác động bên ngoài.

Người dùng luôn giữ quyền quyết định cuối cùng.

---

# 3. Target Persona

## Primary Persona

Người trẻ từ 18–30 tuổi thường xuyên giao tiếp và xây dựng nhiều mối quan hệ.

Ví dụ:

* Sales;
* Freelancer;
* Founder;
* Recruiter;
* Chủ shop online;
* Người làm networking;
* Sinh viên thường xuyên tham gia dự án và cộng đồng.

## Characteristics

Người dùng:

* có nhiều cuộc hội thoại;
* có hàng chục đến hàng trăm contact;
* thường xuyên thêm contact mới;
* phải nhớ nhiều thông tin về từng người;
* không có thói quen ghi chú thủ công;
* thường phải tìm lại thông tin từ lịch sử chat.

---

# 4. Core Problem

Người dùng giao tiếp với quá nhiều người nhưng không thể ghi nhớ đầy đủ:

* người này là ai;
* đã gặp ở đâu;
* làm công việc gì;
* đang quan tâm vấn đề gì;
* lần cuối trao đổi khi nào;
* đã hứa hoặc thống nhất điều gì;
* nên follow-up người nào;
* có mối liên hệ nào có thể tạo ra cơ hội mới.

Việc tìm lại thông tin hiện nay chủ yếu dựa vào:

```text
Search keyword
        ↓
Scroll message
        ↓
Read manually
        ↓
Remember context
```

Quá trình này tốn thời gian và dễ bỏ sót thông tin.

MemoryChat chuyển thành:

```text
Natural Language Query
        ↓
AI Context Retrieval
        ↓
Relevant Memory
        ↓
AI Recommendation
        ↓
User Action
```

---

# 5. Product Scope

## 5.1. MVP Features

MVP gồm:

1. Authentication
2. 1-to-1 Chat
3. Contact Management
4. Contact Memory
5. Conversation Memory
6. Context Recall
7. Semantic Search
8. Recommendation Agent
9. AI Copilot trong conversation
10. Event-driven AI processing

---

# 6. Out of Scope

Trong MVP 6 tuần không triển khai:

* Voice Call;
* Video Call;
* Story;
* Sticker marketplace;
* Payment;
* Public social feed;
* Large-scale group chat;
* AI tự động gửi message;
* AI tự động kết bạn;
* AI tự động giới thiệu hai contact;
* Autonomous Agent thực hiện hành động ngoài hệ thống.

---

# 7. High-level System Architecture

```text
                         Flutter App
                              │
                    REST API + WebSocket
                              │
                              ▼
                       FastAPI Backend
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
            PostgreSQL                  Redis
                 │                         │
                 │                    Event / Queue
                 │                         │
                 └────────────┬────────────┘
                              │
                              ▼
                       AI Orchestrator
                              │
                        LangGraph
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
 Memory Agent          Search Agent       Recommendation Agent
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                        Context Builder
                              │
             ┌────────────────┼─────────────────┐
             │                │                 │
             ▼                ▼                 ▼
           Qdrant           Neo4j             LLM
        Vector Store      Knowledge Graph    Gemini/GPT
```

---

# 8. Technology Stack

## Frontend

Khuyến nghị:

```text
Flutter
```

Lý do:

* phù hợp với messaging application;
* mobile-first;
* dễ demo;
* có thể mở rộng Android/iOS;
* WebSocket support tốt.

---

## Backend

```text
Python
FastAPI
```

FastAPI chịu trách nhiệm:

* REST API;
* WebSocket;
* authentication;
* conversation;
* message;
* contact;
* recommendation;
* AI API;
* event publishing.

---

## AI Orchestration

```text
LangGraph
LangChain
```

LangGraph được sử dụng cho các workflow có nhiều bước.

---

## LLM

MVP:

```text
Gemini 2.5 Flash
```

Có thể abstraction qua LLM Gateway để sau này thay bằng:

* GPT;
* Claude;
* local model.

---

## Embedding

Khuyến nghị:

```text
BGE-M3
```

hoặc embedding API tương ứng.

---

## Vector Database

```text
Qdrant
```

Dùng cho:

* semantic search;
* conversation retrieval;
* memory retrieval;
* recommendation similarity.

---

## Graph Database

```text
Neo4j
```

Dùng cho:

* relationship graph;
* shared interest;
* shared company;
* connection recommendation;
* relationship reasoning.

---

## Relational Database

```text
PostgreSQL
```

Đây là **Source of Truth** của hệ thống.

Lưu:

* User;
* Conversation;
* Participant;
* Message;
* Contact;
* Memory;
* Recommendation;
* Event;
* Settings.

---

## Cache / Event

```text
Redis
```

Dùng cho:

* realtime pub/sub;
* event queue;
* cache;
* rate limiting;
* worker coordination.

---

# 9. Chat Data Architecture

Một conversation không được xác định bằng sender và receiver trực tiếp trong Message.

Cấu trúc:

```text
User
  │
  ▼
Conversation
  │
  ▼
ConversationParticipant
  │
  ▼
Message
```

## User

```text
User
- id
- name
- email
- password_hash
- avatar_url
- created_at
- updated_at
```

---

## Conversation

```text
Conversation
- id
- type
- created_at
- updated_at
```

MVP chỉ sử dụng:

```text
type = private
```

---

## ConversationParticipant

```text
ConversationParticipant
- id
- conversation_id
- user_id
- joined_at
- last_read_message_id
```

Ví dụ:

```text
Conversation 101

User 1
User 2
```

=> Conversation 101 là chat giữa User 1 và User 2.

---

## Message

```text
Message
- id
- conversation_id
- sender_id
- content
- message_type
- created_at
- updated_at
```

`sender_id` cho biết ai gửi.

`conversation_id` cho biết message thuộc cuộc hội thoại nào.

---

# 10. Message Flow

Khi User A gửi message:

```text
Flutter
   │
   ▼
WebSocket
   │
   ▼
FastAPI
   │
   ├── Validate
   │
   ├── Save Message
   │
   └── Publish Event
```

Message được lưu ngay vào PostgreSQL.

Sau đó:

```text
MESSAGE_CREATED
        │
        ├──────────────► WebSocket
        │                   │
        │                   ▼
        │              Receiver UI
        │
        ▼
Redis Event
        │
        ▼
Background Workers
```

Chat không chờ AI xử lý.

---

# 11. Realtime Architecture

Realtime Chat sử dụng:

```text
WebSocket
+
Redis Pub/Sub
```

## Critical Path

```text
Send Message
     ↓
PostgreSQL
     ↓
Redis
     ↓
WebSocket
     ↓
Receiver
```

Không gọi LLM trong critical path.

Mục tiêu:

```text
Message delivery < 300ms
```

trong điều kiện demo/infrastructure bình thường.

---

# 12. AI Processing Architecture

AI processing chạy bất đồng bộ.

```text
Message Created
      ↓
Event
      ↓
Redis
      ↓
Worker
      ↓
Trigger Manager
      ↓
Should Update?
      ↓
Memory Workflow
```

Không chạy AI sau mỗi message.

---

# 13. Memory Architecture

Memory được chia thành hai loại chính.

## 13.1. Conversation Memory

Lưu thông tin của một cuộc hội thoại.

Ví dụ:

```text
Conversation:
Khương ↔ Minh

Summary:
Hai người đang trao đổi về tuyển AI Engineer.

Recent Topic:
AI Recruitment

Decision:
Hẹn trao đổi vào thứ Sáu.
```

Schema:

```text
ConversationMemory
- id
- conversation_id
- summary
- current_topics
- last_processed_message_id
- updated_at
```

---

## 13.2. Contact Memory

Lưu thông tin lâu dài về một contact.

Ví dụ:

```text
Minh

Profession:
Founder

Company:
ABC AI

Interest:
Computer Vision
LLM

Relationship:
Professional

Relationship Score:
0.82
```

Schema:

```text
ContactMemory
- id
- owner_id
- contact_id
- summary
- profession
- company
- skills
- interests
- location
- relationship_score
- updated_at
```

Memory có ownership.

Ví dụ:

```text
Khương → Minh
```

và

```text
Minh → Khương
```

là hai memory khác nhau.

---

# 14. Raw Message vs Memory

PostgreSQL lưu raw message.

Memory không thay thế message.

```text
Raw Message
=
Source of Truth
```

Memory là dữ liệu được AI suy luận từ raw message.

Nếu AI tạo summary sai, hệ thống vẫn có thể quay lại message gốc để kiểm tra.

---

# 15. Incremental Memory

Memory không đọc lại toàn bộ conversation.

Ví dụ:

```text
Conversation có 50,000 messages.

Last processed:
48,000
```

Khi có message mới:

```text
48,001 → 48,030
```

Worker chỉ xử lý:

```text
48,001 → 48,030
```

Sau đó merge vào memory hiện tại.

---

# 16. Memory Trigger System

Memory không được trigger trực tiếp mỗi khi:

```text
CHAT_OPENED
CHAT_CLOSED
```

vì người dùng có thể mở/đóng liên tục.

Hệ thống sử dụng:

```text
Event
+
Threshold
+
Idle Detection
+
Debounce
```

## Trigger 1

Có nhiều message mới.

Ví dụ:

```text
pending_message_count >= 10
```

---

## Trigger 2

Conversation idle.

Ví dụ:

```text
idle_time >= 30 minutes
```

---

## Trigger 3

User yêu cầu cập nhật memory.

```text
Refresh AI Memory
```

---

## Trigger 4

Periodic fallback.

Ví dụ:

```text
Nightly synchronization
```

---

# 17. Debounce

Khi user đóng conversation:

```text
CHAT_CLOSED
```

không chạy AI ngay.

Hệ thống chờ:

```text
60 seconds
```

Nếu user mở lại:

```text
CHAT_OPENED
```

cancel processing.

Nếu user không quay lại:

```text
Trigger Memory
```

---

# 18. Memory Worker State

ConversationMemory cần:

```text
last_processed_message_id
pending_message_count
last_update_at
is_processing
```

Worker đảm bảo:

```text
is_processing = true
```

để tránh hai worker xử lý cùng conversation.

---

# 19. Memory Workflow

```text
MESSAGE_CREATED
       ↓
Increment pending_message_count
       ↓
Trigger Manager
       ↓
Condition satisfied?
       ↓
YES
       ↓
Fetch unprocessed messages
       ↓
Load previous Conversation Memory
       ↓
LLM
       ↓
Generate updated summary
       ↓
Extract entities
       ↓
Update Contact Memory
       ↓
Generate embeddings
       ↓
Update Qdrant
       ↓
Update Neo4j
       ↓
Reset pending count
       ↓
Update last_processed_message_id
```

---

# 20. AI Agents

MemoryChat có 4 AI workflow chính.

## Agent 1 — Memory Agent

Nhiệm vụ:

* summarize;
* extract information;
* update memory;
* build timeline.

---

## Agent 2 — Tagging Agent

Nhiệm vụ:

* extract company;
* profession;
* skill;
* location;
* interest;
* suggest tags.

Tag có thể yêu cầu Human-in-the-loop.

---

## Agent 3 — Search Agent

Nhiệm vụ:

* hiểu natural language query;
* semantic retrieval;
* context retrieval;
* answer query.

---

## Agent 4 — Recommendation Agent

Nhiệm vụ:

* follow-up recommendation;
* priority contact;
* suggested reply;
* tag recommendation;
* contact management;
* connection recommendation.

---

# 21. AI Copilot

AI Copilot là module riêng, không thay thế 4 workflow AI chính.

Copilot nằm trực tiếp trong conversation.

UI có thể giống:

```text
┌─────────────────────────────┐
│ Conversation               │
│                             │
│ User: Hello                 │
│ Contact: Hi                 │
│                             │
│                     [ AI ]  │
└─────────────────────────────┘
```

User có thể mở AI Copilot.

---

# 22. Conversation Sharing với Copilot

Copilot không mặc định có quyền đọc toàn bộ conversation.

User phải chủ động:

```text
Open AI Copilot
       ↓
Share Conversation
       ↓
Select context
       ↓
AI receives selected context
```

Có thể chọn:

* message hiện tại;
* một số message;
* recent conversation;
* toàn bộ conversation.

---

# 23. Copilot Visibility

Nếu User sử dụng Copilot trong conversation:

```text
User A
   │
   ▼
AI Copilot
```

Conversation gốc vẫn là:

```text
User A ↔ User B
```

AI không trở thành participant mặc định.

Nội dung Copilot:

```text
private to User A
```

trừ khi User chủ động gửi/share kết quả vào conversation.

User B không nhìn thấy hoạt động nội bộ của Copilot.

---

# 24. Copilot Use Cases

Ví dụ:

```text
"Tóm tắt cuộc trò chuyện này."

"Người này đang quan tâm điều gì?"

"Trước đây tôi đã hứa gì với người này?"

"Gợi ý cách trả lời."

"Viết một tin nhắn follow-up."

"Tìm trong cuộc trò chuyện xem họ có đề cập deadline không."
```

AI chỉ đưa suggestion.

User quyết định gửi.

---

# 25. Context Builder

Context Builder là thành phần trung tâm của AI Architecture.

Agent không đọc toàn bộ lịch sử chat.

Context Builder quyết định:

```text
Agent cần context nào?
```

Nguồn context:

```text
Recent Messages
Conversation Memory
Contact Memory
Semantic Search
Knowledge Graph
User Profile
Recommendation
```

---

# 26. Dynamic Context Retrieval

Ví dụ User hỏi:

```text
"Người này là ai?"
```

Context:

```text
Contact Memory
+
Profile
```

---

Nếu hỏi:

```text
"Lần trước chúng ta nói gì?"
```

Context:

```text
Conversation Memory
+
Recent Messages
```

---

Nếu hỏi:

```text
"Anh ấy từng nói về AI Agent chưa?"
```

Context:

```text
Semantic Search
+
Relevant Messages
```

---

Nếu hỏi:

```text
"Tôi nên follow-up thế nào?"
```

Context:

```text
Contact Memory
+
Conversation Memory
+
Last Interaction
+
Recommendation
```

---

# 27. Semantic Search

Search pipeline:

```text
User Query
      ↓
Query Understanding
      ↓
Embedding
      ↓
Qdrant
      ↓
Top K Results
      ↓
Reranking
      ↓
LLM
      ↓
Answer
```

Ví dụ:

```text
"Tìm người làm AI ở Hà Nội"
```

Không cần keyword matching chính xác.

AI tìm theo semantic meaning.

---

# 28. Vector Storage

Qdrant lưu embedding của:

* conversation chunks;
* memory;
* relevant contact information;
* important events.

Không lưu PostgreSQL thay thế.

PostgreSQL vẫn là source of truth.

Qdrant chỉ là retrieval index.

---

# 29. Knowledge Graph

Neo4j mô hình hóa quan hệ.

## Nodes

```text
User
Contact
Company
Skill
Interest
Topic
Location
Project
Organization
```

## Relationships

```text
WORK_AT
INTEREST_IN
HAS_SKILL
KNOW
MET_AT
MENTIONED
CONNECTED_TO
FOLLOWED_UP
```

Ví dụ:

```text
Minh
 ↓
WORK_AT
 ↓
ABC AI
 ↓
WORKS_ON
 ↓
Computer Vision
```

---

# 30. Recommendation Architecture

Recommendation Agent sử dụng:

```text
Contact Memory
+
Conversation Memory
+
User Events
+
Knowledge Graph
+
Vector Similarity
+
Interaction History
```

---

# 31. Follow-up Recommendation

Ví dụ:

```text
Contact:
Minh

Last interaction:
45 days ago

Previous topic:
AI Engineer recruitment

Relationship:
High value
```

AI có thể đề xuất:

```text
"Bạn có thể follow-up Minh về vị trí AI Engineer."
```

AI không tự gửi.

---

# 32. Connection Recommendation

Đây không phải Friend Recommendation giống Facebook.

Mục tiêu là phát hiện cơ hội kết nối.

Ví dụ:

```text
Contact A
Founder
AI Startup
Looking for AI Engineer

        +

Contact B
AI Engineer
Looking for Startup Opportunity
```

Recommendation:

```text
Bạn có thể giới thiệu A với B.
```

User phải approve.

---

# 33. Recommendation Human-in-the-loop

Recommendation có trạng thái:

```text
PENDING
ACCEPTED
REJECTED
DISMISSED
```

Không được tự động thực hiện action.

---

# 34. Event-driven Architecture

Các thao tác của User tạo Event.

Ví dụ:

```text
MESSAGE_CREATED
CHAT_OPENED
CHAT_CLOSED
SEARCH_PERFORMED
CONTACT_VIEWED
TAG_ACCEPTED
TAG_REJECTED
RECOMMENDATION_ACCEPTED
RECOMMENDATION_REJECTED
MESSAGE_SENT
MESSAGE_READ
CONTACT_UPDATED
```

Event được lưu:

```text
EventLog
```

và publish qua Redis.

---

# 35. Event Flow

```text
User Action
    ↓
FastAPI
    ↓
Database
    ↓
Event
    ↓
Redis
    ↓
Worker
    ↓
AI / Recommendation / Graph
```

Event không được dùng để thay thế transactional database.

PostgreSQL vẫn là source of truth.

---

# 36. Database Overview

## PostgreSQL

```text
users
conversations
conversation_participants
messages
contacts
conversation_memories
contact_memories
tags
contact_tags
recommendations
events
settings
search_history
```

---

# 37. Core Tables

## users

```text
id
name
email
password_hash
avatar_url
created_at
updated_at
```

## conversations

```text
id
type
created_at
updated_at
```

## conversation_participants

```text
id
conversation_id
user_id
joined_at
last_read_message_id
```

## messages

```text
id
conversation_id
sender_id
content
message_type
created_at
updated_at
```

## contacts

```text
id
owner_id
contact_user_id
display_name
notes
created_at
updated_at
```

## conversation_memories

```text
id
conversation_id
summary
current_topics
last_processed_message_id
pending_message_count
last_update_at
is_processing
```

## contact_memories

```text
id
owner_id
contact_id
summary
profession
company
skills
interests
location
relationship_score
updated_at
```

## recommendations

```text
id
owner_id
contact_id
type
reason
confidence
status
created_at
expires_at
```

## event_logs

```text
id
user_id
event_type
entity_type
entity_id
payload
created_at
```

---

# 38. Data Ownership

MemoryChat phải đảm bảo user isolation.

Ví dụ:

```text
User A
```

chỉ được truy cập:

```text
A's conversations
A's contacts
A's memories
A's recommendations
A's events
```

Không được truy cập memory riêng của User B.

---

# 39. Privacy

Chat là dữ liệu nhạy cảm.

AI processing cần:

* user consent;
* clear settings;
* ability to disable AI memory;
* ability to delete memory;
* ability to delete conversation;
* access control.

AI không được tự ý expose nội dung conversation này sang user khác.

---

# 40. AI Data Isolation

Khi User A hỏi AI:

```text
"Minh là ai?"
```

Context Builder chỉ được retrieve:

```text
User A's memory about Minh
```

Không được lấy:

```text
User B's private memory about Minh
```

---

# 41. Security

Backend phải có:

* JWT authentication;
* password hashing;
* authorization;
* input validation;
* rate limiting;
* API authentication;
* WebSocket authentication;
* SQL injection protection;
* prompt injection protection;
* access control.

---

# 42. Prompt Injection

Conversation có thể chứa câu:

```text
Ignore previous instructions...
```

Agent phải coi conversation content là:

```text
UNTRUSTED USER DATA
```

không phải system instruction.

---

# 43. AI Output Validation

LLM output không được đưa trực tiếp vào database.

Pipeline:

```text
LLM
 ↓
JSON Schema Validation
 ↓
Business Validation
 ↓
Database
```

Ví dụ Recommendation phải có:

```text
type
reason
confidence
contact_id
```

---

# 44. AI Workflow Orchestration

LangGraph được sử dụng để điều phối workflow.

Ví dụ Memory:

```text
START
 ↓
Load Messages
 ↓
Load Previous Memory
 ↓
Extract Information
 ↓
Summarize
 ↓
Validate
 ↓
Update Memory
 ↓
Generate Embedding
 ↓
Update Graph
 ↓
END
```

---

# 45. AI Failure Handling

Nếu LLM lỗi:

```text
Message vẫn được lưu.
```

Chat không bị ảnh hưởng.

AI Worker:

```text
Retry
 ↓
Retry
 ↓
Dead Letter / Failed Job
```

Memory cũ vẫn giữ nguyên.

---

# 46. Async Processing

AI tasks phải chạy background.

Ví dụ:

```text
Message Processing
Memory Update
Embedding
Graph Update
Recommendation
```

không block API request.

---

# 47. Worker Architecture

MVP có thể sử dụng:

```text
FastAPI
+
Redis
+
Background Worker
```

Không cần microservice quá sớm.

Có thể tổ chức:

```text
backend/
    api/
    services/
    repositories/
    workers/
    agents/
    workflows/
    prompts/
    models/
    schemas/
```

---

# 48. Backend Architecture

Khuyến nghị:

```text
API Layer
    ↓
Service Layer
    ↓
Repository Layer
    ↓
Database
```

AI:

```text
AI Service
    ↓
Agent
    ↓
Workflow
    ↓
Tool
    ↓
External Model / DB
```

---

# 49. Repository Pattern

Không để API trực tiếp query database.

Sai:

```text
API
 ↓
SQL
```

Đúng:

```text
API
 ↓
Service
 ↓
Repository
 ↓
PostgreSQL
```

---

# 50. API Categories

## Authentication

```text
POST /auth/register
POST /auth/login
GET /auth/me
```

## Conversation

```text
GET /conversations
GET /conversations/{id}
POST /conversations
```

## Messages

```text
GET /conversations/{id}/messages
POST /conversations/{id}/messages
```

Realtime:

```text
/ws
```

## Contact

```text
GET /contacts
GET /contacts/{id}
PATCH /contacts/{id}
```

## Search

```text
POST /search
```

## Recommendation

```text
GET /recommendations
POST /recommendations/{id}/accept
POST /recommendations/{id}/reject
```

## AI

```text
POST /ai/copilot
POST /ai/memory/refresh
```

---

# 51. Frontend Architecture

Flutter:

```text
Presentation
 ↓
State Management
 ↓
Repository
 ↓
API / WebSocket
```

Các màn hình chính:

```text
Login
Home
Conversation List
Chat
Contacts
Search
Recommendations
Profile
Settings
AI Copilot
```

---

# 52. Chat UI

Chat screen gồm:

```text
Header
 ├── Contact
 ├── Status
 └── AI Context Button

Message List

Message Composer
 ├── Text
 ├── Send
 └── AI Copilot
```

---

# 53. Context Recall UI

Khi mở conversation:

```text
┌──────────────────────────┐
│ AI Context               │
├──────────────────────────┤
│ Minh – Founder           │
│                          │
│ Interested in AI         │
│ Works at ABC AI          │
│                          │
│ Last topic: Recruitment  │
└──────────────────────────┘
```

User có thể mở rộng để xem chi tiết.

---

# 54. Recommendation UI

Recommendation không được chiếm toàn bộ giao diện.

Ví dụ:

```text
AI Suggestion

Bạn đã 45 ngày chưa liên hệ Minh.

Lần cuối hai người nói về
AI Engineer recruitment.

[Follow up] [Dismiss]
```

---

# 55. Connection Recommendation UI

```text
Possible Connection

Minh
Founder – ABC AI

        ↕

An
AI Engineer

Cả hai có thể phù hợp với
nhu cầu hiện tại.

[View] [Dismiss]
```

User quyết định có hành động hay không.

---

# 56. AI Copilot UI

Copilot có thể mở bằng floating button:

```text
       ┌───────┐
       │  AI   │
       └───────┘
```

Khi mở:

```text
AI Copilot

What can I help with?

[Summarize]
[Find information]
[Suggest reply]
[Follow-up]
[Ask AI]
```

Có nút:

```text
Share Conversation
```

để user quyết định context nào được đưa vào Copilot.

---

# 57. Observability

Hệ thống cần log:

```text
API latency
WebSocket connection
Message delivery
Worker status
LLM latency
LLM error
Token usage
Recommendation generation
Memory update
```

Không log raw private message vào monitoring log nếu không cần thiết.

---

# 58. Performance Targets

## Chat

```text
Message delivery < 300ms
```

## Search

```text
< 3 seconds
```

## Context Recall

```text
< 3 seconds
```

## AI Summary

```text
Target < 10 seconds
```

AI processing không được block message delivery.

---

# 59. AI Metrics

## Summary Acceptance Rate

Mục tiêu:

```text
> 80%
```

## Recommendation CTR

Mục tiêu:

```text
> 60%
```

## Search Success Rate

Theo dõi:

```text
Search → User opens correct contact
```

## Context Retrieval Time

Mục tiêu:

```text
< 30 seconds
```

so với việc tìm thủ công.

---

# 60. Product Metrics

Theo dõi:

```text
DAU
WAU
Retention
Search usage
Memory usage
Recommendation acceptance
Follow-up action
Copilot usage
```

---

# 61. AI Quality Evaluation

Không chỉ đánh giá bằng latency.

Memory cần đánh giá:

```text
Correctness
Completeness
Relevance
Consistency
```

Recommendation:

```text
Relevance
Precision
Acceptance
Action Rate
```

Search:

```text
Retrieval Precision
Answer Relevance
User Success
```

---

# 62. Deployment

MVP có thể triển khai:

```text
Flutter App
      │
      ▼
Cloud / VPS
      │
      ├── FastAPI
      ├── PostgreSQL
      ├── Redis
      ├── Qdrant
      └── Neo4j
```

LLM sử dụng external API.

Không cần self-host LLM trong MVP.

---

# 63. Docker

Các service có thể chạy bằng:

```text
docker-compose
```

Ví dụ:

```text
backend
postgres
redis
qdrant
neo4j
worker
```

Điều này giúp toàn bộ team có môi trường giống nhau.

---

# 64. Development Strategy

6 tuần chia thành:

## Week 1

Foundation:

* database;
* authentication;
* backend structure;
* Flutter setup;
* basic chat.

## Week 2

Realtime:

* WebSocket;
* message persistence;
* contact;
* conversation.

## Week 3

Memory:

* Memory Agent;
* Conversation Memory;
* Contact Memory;
* incremental update.

## Week 4

AI Search:

* embedding;
* Qdrant;
* semantic search;
* Context Builder.

## Week 5

Recommendation + Copilot:

* Recommendation Agent;
* connection recommendation;
* follow-up;
* AI Copilot;
* share conversation.

## Week 6

Integration:

* testing;
* UI polish;
* performance;
* security;
* demo scenario;
* deployment.

---

# 65. MVP Simplification Rules

Nếu thiếu thời gian, ưu tiên theo thứ tự:

```text
1. Chat
2. Memory
3. Context Recall
4. Search
5. Recommendation
6. Copilot
7. Knowledge Graph enhancement
```

Không hy sinh:

```text
Message persistence
Authentication
Data isolation
Memory correctness
```

---

# 66. Recommended MVP Architecture

Kiến trúc cuối cùng:

```text
                         FLUTTER
                            │
                   REST + WebSocket
                            │
                            ▼
                       FASTAPI
                            │
             ┌──────────────┼───────────────┐
             │              │               │
             ▼              ▼               ▼
        PostgreSQL        Redis         AI Service
             │              │               │
             │              │            LangGraph
             │              │               │
             │              │      ┌────────┼────────┐
             │              │      │        │        │
             │              │      ▼        ▼        ▼
             │              │   Memory   Search  Recommendation
             │              │    Agent    Agent      Agent
             │              │      │        │        │
             │              │      └────────┼────────┘
             │              │               │
             │              │        Context Builder
             │              │               │
             │              │       ┌───────┴────────┐
             │              │       │                │
             ▼              ▼       ▼                ▼
         Messages         Events   Qdrant           Neo4j
                                 Vector DB        Graph DB
                                      │                │
                                      └───────┬────────┘
                                              ▼
                                             LLM
```

---

# 67. Core Design Principle

MemoryChat phải tuân thủ nguyên tắc:

```text
REALTIME CHAT
≠
AI PROCESSING
```

Chat phải nhanh.

AI có thể xử lý bất đồng bộ.

---

# 68. Core Data Principle

```text
PostgreSQL
=
Source of Truth
```

Qdrant:

```text
Retrieval Index
```

Neo4j:

```text
Relationship Intelligence
```

Redis:

```text
Realtime + Event Infrastructure
```

LLM:

```text
Reasoning Engine
```

Memory:

```text
AI-derived knowledge
```

---

# 69. Core AI Principle

Agent không tự đọc toàn bộ database.

Agent nhận:

```text
User Query
+
Relevant Context
```

Context được xây dựng bởi:

```text
Context Builder
```

Context Builder lấy dữ liệu từ:

```text
Recent Messages
Conversation Memory
Contact Memory
Qdrant
Neo4j
Recommendation
```

---

# 70. Final System Flow

Toàn bộ hệ thống có thể tóm tắt:

```text
USER
 │
 ▼
CHAT
 │
 ▼
POSTGRESQL
 │
 ▼
EVENT
 │
 ▼
REDIS
 │
 ▼
TRIGGER MANAGER
 │
 ├── Not enough context → WAIT
 │
 └── Trigger satisfied
          │
          ▼
     MEMORY AGENT
          │
          ├── Conversation Memory
          ├── Contact Memory
          ├── Embedding
          └── Knowledge Graph
                    │
                    ▼
             RECOMMENDATION
                    │
                    ▼
                USER
```

Khi User cần hỏi AI:

```text
USER QUERY
    │
    ▼
CONTEXT BUILDER
    │
    ├── Recent Messages
    ├── Conversation Memory
    ├── Contact Memory
    ├── Qdrant
    └── Neo4j
    │
    ▼
LLM
    │
    ▼
ANSWER / RECOMMENDATION
    │
    ▼
USER
```

---

# 71. Architectural Decision Summary

| Decision        | Choice                   |
| --------------- | ------------------------ |
| Client          | Flutter                  |
| Backend         | FastAPI                  |
| Main DB         | PostgreSQL               |
| Realtime        | WebSocket                |
| Event/Cache     | Redis                    |
| Vector DB       | Qdrant                   |
| Graph DB        | Neo4j                    |
| LLM             | Gemini 2.5 Flash         |
| Agent Framework | LangGraph                |
| Embedding       | BGE-M3                   |
| Memory          | Incremental              |
| Memory Trigger  | Event + Threshold + Idle |
| Chat Storage    | Immediate                |
| AI Processing   | Async                    |
| Recommendation  | Human-in-the-loop        |
| AI Copilot      | Separate module          |
| AI Context      | Dynamic Context Builder  |
| Raw Message     | Source of Truth          |
| AI Action       | Suggest only             |

---

# 72. Final Product Definition

MemoryChat không đơn giản là:

```text
Chat + Chatbot
```

Mà là:

```text
Messaging Platform
        +
Long-term Memory
        +
Semantic Search
        +
Relationship Intelligence
        +
Recommendation
        +
AI Copilot
```

Trong đó:

```text
Chat
 ↓
Data
 ↓
Memory
 ↓
Knowledge
 ↓
Recommendation
 ↓
Action
```

là vòng lặp cốt lõi của sản phẩm.

Mục tiêu cuối cùng là biến một ứng dụng chat thông thường thành một hệ thống có khả năng **ghi nhớ và hiểu các mối quan hệ của người dùng theo thời gian**, nhưng vẫn đảm bảo người dùng kiểm soát hoàn toàn dữ liệu và hành động của AI.
