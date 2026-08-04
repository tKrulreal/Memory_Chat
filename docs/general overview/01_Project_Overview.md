# MemoryChat

> AI-native Messaging Platform with Long-term Relationship Memory

Version: MVP v1.0

Project Type: AI Application

Duration: 6 Weeks

Target Program: VinUni AI Thực Chiến

---

# 1. Introduction

## 1.1 Project Overview

MemoryChat là một nền tảng nhắn tin tích hợp AI được xây dựng với mục tiêu giúp người dùng quản lý và khai thác giá trị từ các mối quan hệ cá nhân và công việc.

Khác với các ứng dụng nhắn tin truyền thống như Messenger, Zalo hay Telegram, MemoryChat không xem dữ liệu hội thoại chỉ là lịch sử tin nhắn.

Mỗi cuộc trò chuyện đều được AI phân tích, ghi nhớ và chuyển đổi thành tri thức có cấu trúc để hỗ trợ người dùng trong tương lai.

Thay vì chỉ lưu "đã nhắn gì", hệ thống cố gắng hiểu:

- Người này là ai
- Hai người quen nhau như thế nào
- Đã từng trao đổi về vấn đề gì
- Người này quan tâm điều gì
- Khi nào nên liên hệ lại
- Có ai phù hợp để giới thiệu với họ không

MemoryChat hướng tới việc trở thành một "Second Brain" dành cho các mối quan hệ.

---

# 2. Vision

## Product Vision

Build an AI-native messaging platform that remembers every relationship, understands every conversation, and proactively assists users in maintaining meaningful connections.

Thay vì để người dùng tự ghi chú hoặc tìm lại lịch sử hội thoại, AI sẽ đóng vai trò như một trợ lý cá nhân giúp:

- Ghi nhớ thông tin
- Tóm tắt ngữ cảnh
- Hiểu mối quan hệ
- Gợi ý hành động
- Hỗ trợ tìm kiếm
- Đề xuất kết nối

Mục tiêu cuối cùng không phải tạo ra chatbot thông minh hơn.

Mục tiêu là giúp người dùng không bao giờ phải tự hỏi:

> "Người này là ai nhỉ?"

hoặc

> "Lần trước mình đã nói gì?"

---

# 3. Product Positioning

MemoryChat KHÔNG phải:

- CRM
- Social Network
- Chatbot
- Personal Note
- Contact Manager

MemoryChat là:

AI Relationship Intelligence Platform.

Chat chỉ là nơi dữ liệu được sinh ra.

AI mới là giá trị cốt lõi của sản phẩm.

---

# 4. Background

Trong quá trình networking, làm việc hoặc bán hàng, người dùng phải duy trì hàng chục đến hàng trăm cuộc trò chuyện cùng lúc.

Theo thời gian, lượng dữ liệu hội thoại tăng rất nhanh.

Một người có thể:

- thêm 5–10 contact mới mỗi tuần
- trao đổi với hàng trăm người
- làm nhiều dự án cùng lúc
- tham gia nhiều cộng đồng

Điều này dẫn đến các vấn đề:

- Không nhớ đã gặp ở đâu.
- Không nhớ công việc của người đó.
- Không nhớ lần cuối nói chuyện.
- Không nhớ đã hứa điều gì.
- Không biết nên liên hệ lại với ai.

Các ứng dụng chat hiện tại chỉ cung cấp chức năng lưu trữ tin nhắn.

Việc hiểu và khai thác dữ liệu vẫn hoàn toàn phụ thuộc vào người dùng.

Đây chính là khoảng trống mà MemoryChat muốn giải quyết.

---

# 5. Product Goal

MemoryChat hướng tới ba mục tiêu chính.

## Goal 1

AI ghi nhớ mọi mối quan hệ.

Mỗi Contact đều có hồ sơ được AI xây dựng tự động.

Bao gồm:

- nghề nghiệp
- công ty
- sở thích
- lĩnh vực
- dự án
- timeline
- lịch sử tương tác

---

## Goal 2

AI giúp người dùng tìm đúng người đúng thời điểm.

Ví dụ:

"Tìm người làm AI ở Hà Nội."

"Tìm khách hàng từng hỏi về chatbot."

"Tìm người từng nhắc đến Computer Vision."

Không cần tìm theo từ khóa.

Người dùng chỉ cần hỏi bằng ngôn ngữ tự nhiên.

---

## Goal 3

AI chủ động đưa ra recommendation.

Ví dụ:

- nên follow-up ai
- nên cập nhật tag nào
- nên merge contact nào
- có ai phù hợp để giới thiệu
- nên ưu tiên khách hàng nào

AI không tự thực hiện.

AI chỉ đưa ra gợi ý.

Người dùng luôn là người quyết định cuối cùng.

---

# 6. Core Value Proposition

MemoryChat mang lại giá trị ở ba lớp.

## Layer 1 — Conversation

Cung cấp khả năng nhắn tin cơ bản.

Đây là nơi tạo dữ liệu.

---

## Layer 2 — Memory

AI chuyển dữ liệu hội thoại thành tri thức.

Ví dụ:

- Summary
- Timeline
- Profile
- Tags
- Relationship

---

## Layer 3 — Intelligence

AI sử dụng tri thức để:

- Search
- Recommend
- Recall Context
- Suggest Reply
- Connection Recommendation

Đây chính là điểm khác biệt của sản phẩm.

---

# 7. Design Principles

Toàn bộ hệ thống được xây dựng theo các nguyên tắc sau.

## AI First

AI là giá trị cốt lõi.

Mọi tính năng đều được thiết kế xoay quanh AI.

---

## Human in the Loop

AI chỉ gợi ý.

Không tự động thực hiện hành động.

---

## Privacy First

Mọi dữ liệu đều thuộc quyền kiểm soát của người dùng.

AI không chia sẻ dữ liệu cho contact khác.

Không tự gửi tin nhắn.

Không tự giới thiệu người.

---

## Explainable Recommendation

Mỗi recommendation phải có lý do.

Ví dụ:

"Đề xuất follow-up vì đã 30 ngày chưa liên hệ."

Thay vì:

"Bạn nên nhắn người này."

---

## Modular AI

Mỗi AI Agent hoạt động độc lập.

Có thể mở rộng dễ dàng trong tương lai.

---

# 8. Target Users

MemoryChat không hướng tới tất cả mọi người.

Đối tượng chính là những người có cường độ giao tiếp cao.

Bao gồm:

- Sales
- Founder
- Freelancer
- Recruiter
- Business Development
- Chủ shop online
- Người làm cộng đồng
- Người thường xuyên networking

Các nhóm người dùng này có chung một vấn đề:

Số lượng mối quan hệ tăng nhanh hơn khả năng ghi nhớ.

---

# 9. Success Criteria

Một MVP thành công khi người dùng có thể:

- tìm đúng contact trong vài giây
- nhớ lại ngữ cảnh mà không cần đọc toàn bộ chat
- biết nên liên hệ với ai tiếp theo
- tận dụng AI để quản lý mối quan hệ thay vì ghi chú thủ công

Nếu AI chỉ đóng vai trò chatbot trả lời câu hỏi, dự án được xem là chưa đạt mục tiêu.

AI phải trở thành "Relationship Intelligence Engine" đứng phía sau toàn bộ trải nghiệm sản phẩm.

---

# 10. MVP Scope

Trong 6 tuần, nhóm chỉ tập trung xây dựng các thành phần tạo ra giá trị AI.

Bao gồm:

- Authentication
- One-to-One Chat
- Contact Management
- Contact Memory
- Context Recall
- Smart Search
- AI Recommendation
- AI Copilot

Không triển khai:

- Voice Call
- Video Call
- Group Chat
- Story
- Sticker
- AI tự gửi tin nhắn
- AI tự động thực hiện hành động

Mọi recommendation đều yêu cầu người dùng xác nhận trước khi áp dụng.

---

# 11. High-Level Architecture

                    MemoryChat

                        │

        ┌───────────────┼───────────────┐

        │                               │

   Messaging Layer               AI Intelligence Layer

        │                               │

   Conversation                  AI Copilot

        │                               │

        └───────────────┬───────────────┘

                        │

               Assistant Orchestrator

                        │

     ┌──────────────┬──────────────┬──────────────┐

     │              │              │              │

 Memory Agent   Search Agent  Tagging Agent  Recommendation Agent

                        │

             PostgreSQL + Neo4j + Qdrant
