# 02_Product_Requirement_Document.md

# Product Requirement Document (PRD)

Project: MemoryChat

Version: MVP v1.0

Owner: Product Team

Duration: 6 Weeks

---

# 1. Product Vision

MemoryChat là một ứng dụng nhắn tin tích hợp AI giúp người dùng quản lý và khai thác giá trị từ các mối quan hệ thông qua dữ liệu hội thoại.

Khác với các ứng dụng chat truyền thống chỉ lưu trữ tin nhắn, MemoryChat sử dụng AI để hiểu nội dung hội thoại, xây dựng hồ sơ cho từng liên hệ và hỗ trợ người dùng trong việc ghi nhớ, tìm kiếm và duy trì các mối quan hệ.

AI trong hệ thống không thay thế người dùng mà đóng vai trò như một trợ lý cá nhân (AI Copilot), luôn sẵn sàng cung cấp ngữ cảnh, gợi ý và recommendation khi cần thiết.

---

# 2. Product Scope

Trong phạm vi MVP kéo dài 6 tuần, sản phẩm tập trung vào việc chứng minh giá trị của AI thay vì xây dựng đầy đủ một ứng dụng nhắn tin.

Các tính năng bắt buộc bao gồm:

- Đăng ký và đăng nhập.
- Danh sách cuộc trò chuyện.
- Nhắn tin 1-1.
- Quản lý danh bạ.
- AI Contact Memory.
- Smart Search.
- Context Recall.
- Recommendation.
- AI Copilot.

Những tính năng sau sẽ không nằm trong MVP:

- Group Chat.
- Voice Call.
- Video Call.
- Story.
- Sticker.
- Livestream.
- AI tự động gửi tin nhắn.
- AI tự động thực hiện hành động.

---

# 3. Product Objectives

MVP cần chứng minh được ba giả thuyết chính.

## Objective 1

AI có thể tự động xây dựng hồ sơ của từng Contact từ lịch sử hội thoại.

Thay vì người dùng phải tự ghi chú:

- AI hiểu người đó là ai.
- AI hiểu nghề nghiệp.
- AI hiểu sở thích.
- AI hiểu những chủ đề đã từng trao đổi.

---

## Objective 2

AI giúp người dùng tìm lại đúng người nhanh hơn rất nhiều so với tìm kiếm truyền thống.

Ví dụ:

"Tìm người từng làm Computer Vision."

"Tìm người đang làm startup."

"Tìm người từng hỏi về chatbot."

Người dùng không cần nhớ chính xác từ khóa.

---

## Objective 3

AI có thể chủ động đưa ra recommendation giúp người dùng duy trì mối quan hệ.

Ví dụ:

- Follow-up Recommendation.
- Suggested Reply.
- Tag Recommendation.
- Connection Recommendation.
- Priority Contact.

---

# 4. User Persona

MemoryChat hướng đến nhóm người dùng có cường độ giao tiếp cao.

Persona chính gồm:

### Sales

Quản lý nhiều khách hàng.

Khó nhớ lịch sử làm việc.

Khó theo dõi nhu cầu từng khách hàng.

---

### Freelancer

Làm việc với nhiều khách hàng cùng lúc.

Không nhớ đã trao đổi ở dự án nào.

---

### Founder

Networking liên tục.

Thường xuyên gặp đối tác.

Khó ghi nhớ thông tin của từng người.

---

### Recruiter

Quản lý hàng trăm ứng viên.

Không nhớ từng cuộc trao đổi.

---

### Business Development

Thường xuyên mở rộng mạng lưới quan hệ.

Cần follow-up đúng thời điểm.

---

# 5. Problem Statement

Người dùng thường xuyên giao tiếp với nhiều người trên ứng dụng chat.

Theo thời gian:

- số lượng cuộc hội thoại tăng lên
- thông tin bị phân tán
- khó tìm lại dữ liệu
- không nhớ người này là ai
- bỏ lỡ cơ hội hợp tác

Việc đọc lại toàn bộ lịch sử chat tốn rất nhiều thời gian.

Hiện nay chưa có ứng dụng nào giúp người dùng quản lý các mối quan hệ bằng AI ngay trong môi trường chat.

---

# 6. User Stories

## Authentication

Là người dùng mới.

Tôi muốn tạo tài khoản.

Để bắt đầu sử dụng ứng dụng.

---

Là người dùng cũ.

Tôi muốn đăng nhập nhanh.

Để tiếp tục các cuộc trò chuyện.

---

## Chat

Là người dùng.

Tôi muốn gửi và nhận tin nhắn.

Để giao tiếp với các contact.

---

## Contact Memory

Là người dùng.

Tôi muốn AI tự ghi nhớ thông tin của từng contact.

Để không phải ghi chú thủ công.

---

## Context Recall

Là người dùng.

Khi mở lại cuộc chat.

Tôi muốn biết ngay:

- người này là ai
- đã nói gì
- lần cuối liên hệ

Để không phải đọc lại lịch sử.

---

## Smart Search

Là người dùng.

Tôi muốn tìm contact bằng ngôn ngữ tự nhiên.

Để không cần nhớ chính xác tên hoặc từ khóa.

---

## Recommendation

Là người dùng.

Tôi muốn AI gợi ý nên follow-up ai.

Để không bỏ lỡ cơ hội.

---

## AI Copilot

Là người dùng.

Tôi muốn có một AI ngay trong cuộc trò chuyện.

Để hỏi bất kỳ điều gì liên quan đến contact hiện tại mà không phải chuyển sang chatbot khác.

---

# 7. Functional Requirements

## Authentication

- Register
- Login
- Logout
- JWT Authentication

---

## Chat

- Conversation List
- Send Message
- Receive Message
- Read Status
- Contact List

---

## Contact Memory

AI tự động xây dựng:

- Summary
- Company
- Profession
- Skills
- Interest
- Timeline
- Relationship Score

Memory chỉ được cập nhật khi có sự kiện phù hợp (Conversation Idle, đủ số lượng tin nhắn, hoặc người dùng yêu cầu), không cập nhật sau mỗi tin nhắn.

---

## Smart Search

Cho phép tìm kiếm bằng ngôn ngữ tự nhiên.

Ví dụ:

"Tìm người từng nói về AI."

"Tìm founder ở Hà Nội."

"Tìm khách hàng ngành giáo dục."

Search sử dụng:

- Embedding
- Vector Search
- LLM

---

## Context Recall

Khi mở cuộc chat.

AI hiển thị:

- Summary
- Last Discussion
- Company
- Tags
- Relationship Score
- Timeline

---

## Recommendation

AI có thể đề xuất:

- Follow-up Recommendation.
- Suggested Reply.
- Tag Recommendation.
- Merge Contact.
- Connection Recommendation.
- Priority Contact.

Tất cả recommendation đều cần người dùng xác nhận.

---

## AI Copilot

Trong mỗi cuộc trò chuyện sẽ có một nút **🤖 AI**.

AI Copilot không phải là chatbot riêng mà là trợ lý theo ngữ cảnh của cuộc trò chuyện hiện tại.

Khi người dùng bấm vào, một bảng điều khiển (Bottom Sheet) sẽ xuất hiện với các tác vụ nhanh:

- Tóm tắt cuộc trò chuyện.
- Hồ sơ liên hệ.
- Gợi ý trả lời.
- Tìm trong hội thoại.
- Tìm trong Contact Memory.
- Gợi ý Follow-up.
- Gợi ý kết nối.
- Hỏi AI bằng ngôn ngữ tự nhiên.

AI Copilot tự động nhận biết `conversation_id`, `contact_id` và ngữ cảnh hiện tại, do đó không cần hỏi lại người dùng đang nói về ai.

Khi AI sinh nội dung (ví dụ gợi ý trả lời hoặc soạn tin nhắn), hệ thống hiển thị hai lựa chọn:

- **Close**: đóng kết quả, không có gì được gửi.
- **Share to Conversation**: chèn nội dung vào ô nhập tin nhắn.

Người dùng vẫn phải nhấn **Send** để gửi. AI không được phép gửi tin nhắn thay người dùng.

---

# 8. Non-functional Requirements

- Search latency < 3 giây.
- Context Recall < 30 giây.
- Hệ thống hỗ trợ tối thiểu 1.000 người dùng.
- API phản hồi dưới 300ms (không tính thời gian LLM).
- AI Recommendation phải có lý do giải thích.
- Toàn bộ thao tác AI phải tuân thủ Human-in-the-loop.
- Dữ liệu của mỗi người dùng được tách biệt, không sử dụng để xây dựng hồ sơ cho người dùng khác.

---

# 9. Acceptance Criteria

Một MVP được coi là hoàn thành khi:

- Người dùng có thể nhắn tin 1-1.
- AI tự tạo Contact Memory.
- AI hiển thị Context Recall khi mở cuộc chat.
- AI tìm kiếm contact bằng ngôn ngữ tự nhiên.
- AI đưa ra Recommendation hợp lý.
- AI Copilot hoạt động trong từng cuộc trò chuyện và có thể chia sẻ nội dung vào cuộc chat thông qua nút "Share to Conversation".
- Không có bất kỳ hành động nào được AI thực hiện tự động mà không có xác nhận của người dùng.

---

# 10. Success Metrics

- Thời gian tìm lại ngữ cảnh < 30 giây.
- Search thành công trong > 90% truy vấn thử nghiệm.
- Tỷ lệ chấp nhận AI Summary > 80%.
- Tỷ lệ người dùng sử dụng Smart Search ít nhất 2 lần trong 7 ngày > 60%.
- Tỷ lệ người dùng sử dụng Recommendation > 50%.
- Điểm hài lòng (CSAT) ≥ 4/5.