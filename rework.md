Các lỗi cần xử lý trước
Mức	Vị trí	Vấn đề	Hậu quả
P0	[src/agents/search/agent.py (line 67)](/E:/26.AI-VIN/projectAi/P-214/src/agents/search/agent.py:67)	Semantic search không nhận/lọc user_id; Chroma query cũng không có ACL.	Có thể trả memory của user khác.
P0	[src/workers/memory_worker.py (line 63)](/E:/26.AI-VIN/projectAi/P-214/src/workers/memory_worker.py:63)	Sau khi gửi tin, last_message_time vừa được cập nhật nên điều kiện idle 5 phút luôn false.	Memory gần như không tự refresh.
P0	[src/workers/memory_worker.py (line 214)](/E:/26.AI-VIN/projectAi/P-214/src/workers/memory_worker.py:214)	Refresh xong không phát MEMORY_UPDATED.	Insight/recommendation không chạy đúng chuỗi.
P0	[src/api/v1/copilot.py (line 183)](/E:/26.AI-VIN/projectAi/P-214/src/api/v1/copilot.py:183)	contact_id/conversation_id từ request không được xác thực đầy đủ trước khi đưa vào agent.	Rủi ro sai scope dữ liệu.
P0	[src/agents/orchestrator.py (line 336)](/E:/26.AI-VIN/projectAi/P-214/src/agents/orchestrator.py:336)	Tool search cần query, nhưng orchestrator chỉ truyền limit, context IDs.	Copilot intent SEARCH thực tế lỗi/fallback.
P0	[src/api/ws.py (line 34)](/E:/26.AI-VIN/projectAi/P-214/src/api/ws.py:34)	JWT ở query string; manager chỉ giữ socket theo conversation trong một process.	Lộ token qua proxy log; không scale nhiều instance.
P1	[src/services/llm.py (line 14)](/E:/26.AI-VIN/projectAi/P-214/src/services/llm.py:14), [src/gateways/llm.py (line 14)](/E:/26.AI-VIN/projectAi/P-214/src/gateways/llm.py:14)	Hai LLMGateway, cả hai ghi prompt/response hội thoại vào .ai-log.	Trùng logic và rò rỉ PII hội thoại vào log.
P1	[src/config.py (line 24)](/E:/26.AI-VIN/projectAi/P-214/src/config.py:24), [src/core/security.py (line 18)](/E:/26.AI-VIN/projectAi/P-214/src/core/security.py:18)	JWT secret có thể đổi sau mỗi restart; thời hạn token hard-code 60 phút, bỏ qua config.	Token không ổn định, config không có tác dụng.


Bộ test hiện tại không chứng minh được P2P: test WebSocket kết nối hai socket bằng cùng một user/token, không phải hai user khác nhau. Tôi chưa chạy được test vì workspace không có Python/pytest khả dụng (py -m pytest báo “No installed Python found”).
Kế hoạch refactor chi tiết
Giai đoạn / vị trí	Sửa gì	Ý nghĩa	Output sau sửa
0. Chốt product contract	Chốt P2P là server-mediated direct message; không hỗ trợ group chat ở bản này; AI là private assistant của từng user.	Không để schema quay lại “user + contact giả”.	Một tài liệu ADR nêu rõ ownership, xóa tin, read receipt, retention, AI consent.
1. Khóa các đường rò dữ liệu	Tạm tắt /api/v1/search, generic /api/v1/chat, và các agent global cho đến khi có scope. Ngừng ghi raw prompt/response vào .ai-log; chỉ log request ID, model, latency, token count và lỗi đã redaction.	Bảo vệ dữ liệu trước khi refactor lớn.	Không endpoint nào có thể semantic-search dữ liệu chéo user; không còn plaintext chat trong app logs.
2. [src/models/chat.py (line 10)](/E:/26.AI-VIN/projectAi/P-214/src/models/chat.py:10) + Alembic	Thay Conversation(user_id, contact_id) bằng direct_conversations(user_a_id, user_b_id, last_message_id, last_message_at); canonicalize cặp A/B và unique pair. Thêm conversation_user_state cho read cursor/archive/mute. Thay Message.sender_type bằng sender_user_id, client_message_id, edited_at, deleted_at.	Hai user cùng nhìn một canonical conversation; sender do server xác định.	Tạo DM A→B hay B→A trả về cùng một conversation ID; không ai giả được sender.
3. [src/models/contact.py (line 25)](/E:/26.AI-VIN/projectAi/P-214/src/models/contact.py:25), [src/models/ai.py (line 8)](/E:/26.AI-VIN/projectAi/P-214/src/models/ai.py:8)	Loại Contact, ContactMemory, Tag, Recommendation nếu mục tiêu chỉ là P2P. Giữ EventLog nhưng chỉ lưu metadata redacted. Thêm assistant_memories(owner_user_id, conversation_id, through_message_id, summary, facts) và outbox_events.	AI memory thuộc riêng user đang dùng assistant, không phải một “hồ sơ contact” chung. Outbox giúp không mất event sau commit.	Xóa user sẽ xóa/ẩn đúng dữ liệu của user; assistant của A không lộ memory riêng của A cho B.
4. Migration dữ liệu	Không tự động biến Contact thành User: bảng hiện tại không có identity đã xác minh của người bên kia. Backup trước; chỉ map khi email trùng với account và có quy tắc xác nhận rõ, còn lại archive/export rồi loại bỏ.	Tránh tạo hội thoại sai người hoặc lộ lịch sử.	Migration có dry-run report: mapped / unmapped / rejected; rollback được trước khi xóa legacy.
5. Services/repositories/schemas	Thay ContactService, ConversationService, MessageService bằng DirectConversationService, DirectMessageService, MembershipPolicy. Tất cả read/write luôn kiểm tra “current user là A hoặc B”. Message create không nhận role từ client.	Quy tắc P2P nằm ở một chỗ, không rải ownership check.	POST message tự gán sender = JWT subject; delete chỉ soft-delete tin do chính người đó gửi.
6. REST API	Giữ auth, nhưng thêm handle public, tìm user theo handle và không trả email. Thay API chat bằng: POST /direct-conversations, GET /conversations, GET /conversations/{id}, GET /conversations/{id}/messages?before=, POST /conversations/{id}/messages, POST /conversations/{id}/read.	Contract trực tiếp phản ánh chat 1–1, cursor pagination và idempotency.	User A tạo/tìm B, gửi message với client_message_id; retry không tạo bản sao; B thấy unread/read state.
7. [src/api/ws.py (line 30)](/E:/26.AI-VIN/projectAi/P-214/src/api/ws.py:30), [src/ws/manager.py (line 7)](/E:/26.AI-VIN/projectAi/P-214/src/ws/manager.py:7)	WebSocket chỉ làm realtime fan-out; gửi tin qua REST để có idempotency/transaction. Xác thực bằng cookie same-site hoặc one-time realtime ticket, không để JWT trên URL. Quản lý kết nối theo user_id; chỉ fan-out message.created, message.read, typing cho hai participant.	REST và WS không còn hai luồng ghi message khác nhau.	Gửi bằng REST vẫn realtime đến B; reconnect dùng cursor để lấy phần bị lỡ; chạy nhiều instance qua Redis pub/sub.
8. [src/events/bus.py (line 20)](/E:/26.AI-VIN/projectAi/P-214/src/events/bus.py:20), workers	Thay EventBus in-memory bằng transactional outbox + worker độc lập; event MESSAGE_CREATED → MEMORY_COMPACTION_REQUESTED → MEMORY_UPDATED. Worker claim job, retry có backoff và idempotency key.	Không mất job khi restart; handler chậm không chặn toàn bộ event queue.	Mỗi message chỉ sinh tối đa một job theo checkpoint; worker restart không tạo trùng memory/notification.
9. Agent	Giữ một LLMGateway tại src/gateways/llm.py, chuyển sang async, structured output, timeout/retry/cost metrics. Bỏ LangGraph generic route; thay bằng use-case hẹp: generate-reply, summarize-conversation, search-own-conversation. Tool nhận server-side scoped context, không tự mở SessionLocal, không nhận scope từ model.	Agent hữu ích nhưng không có quyền tự do quét DB hay tạo message thay user.	Một request AI chỉ đọc đúng conversation mà user là participant; suggestion không tự gửi tin.
10. Memory/vector	Refactor [MemoryAgent (line 141)](/E:/26.AI-VIN/projectAi/P-214/src/agents/memory/agent.py:141) theo owner_user_id + conversation_id + checkpoint. Nếu giữ vector search, metadata bắt buộc có owner và query bắt buộc filter owner; production dùng PostgreSQL + pgvector, MVP SQLite dùng FTS trước.	Chặn cross-tenant retrieval và tránh Chroma state khó kiểm soát.	Search AI của A không thể truy xuất document của B dù biết ID.
11. Security/config	Require JWT_SECRET cố định ở production, dùng settings.jwt_expire_minutes, rate limit auth/message/AI, giới hạn CORS production, validate password/handle, trả lỗi chuẩn không leak exception.	Điều kiện tối thiểu để public P2P app.	Restart không logout toàn bộ user; auth/message abuse bị giới hạn; health không lộ DB error chi tiết ở production.
12. Test, observability, docs	Viết test contract/DB/WS thật với hai user độc lập; race tạo DM; forged sender; unauthorized third user; idempotency; REST→WS delivery; reconnect; outbox retry; AI scope; deletion/vector cleanup. Viết lại specs và OpenAPI.	Test chuyển từ “mock đúng code” sang chứng minh invariants sản phẩm.	CI chạy migration + full suite; docs không còn mô tả conversation_pairs trong khi schema thực tế không có bảng này.


API nên xóa hoặc thay thế
Xóa hoàn toàn nếu chuyển hẳn sang P2P:
/api/v1/chat, /api/v1/status từ [src/api/routes.py (line 9)](/E:/26.AI-VIN/projectAi/P-214/src/api/routes.py:9)
Toàn bộ /api/v1/contacts/* từ [contacts.py (line 44)](/E:/26.AI-VIN/projectAi/P-214/src/api/v1/contacts.py:44)
Toàn bộ /api/v1/memory/* theo contact_id
Toàn bộ /api/v1/recommendations/*
Toàn bộ /api/v1/connections/*
/api/v1/search global
/api/v1/copilot/share vì hiện tạo message USER/draft trực tiếp trên server, và /api/v1/copilot/intents
Thay đổi, không xóa:
/conversations: tạo bằng recipient_user_id, không nhận contact_id, không cho “delete shared conversation”.
/messages: không nhận role; sender lấy từ JWT.
/notifications: chỉ giữ nếu phục vụ push/system notification; không còn recommendation CRM.
/copilot: chuyển thành endpoint nằm dưới conversation, ví dụ POST /conversations/{id}/assistant/reply-suggestions.
Xóa code tương ứng sau khi migration cutover: src/agents/connection/, src/agents/tagging/, src/agents/recommendation/, src/agents/insight/, các contact/recommendation repositories/services/schemas, src/agents/graph.py, src/agents/nodes/example_node.py, src/agents/tools/example_tool.py, và src/services/llm.py trùng gateway.
Tiêu chí nghiệm thu cuối cùng
A và B là hai account thật, tạo DM theo hai chiều luôn nhận cùng conversation.
Tin nhắn luôn có sender_user_id do backend gán; user thứ ba bị từ chối ở REST, WebSocket, AI và search.
Gửi qua REST được B nhận realtime; retry request không tạo tin nhắn trùng.
Worker/AI không làm chậm gửi tin và không mất job khi restart.
AI chỉ tạo suggestion/private memory; không tự gửi tin, không đọc dữ liệu ngoài scope.
Không còn endpoint/model/agent “Contact CRM” nếu sản phẩm đã chọn thuần P2P.
Nếu bạn xác nhận hướng “direct messaging qua server, không E2EE” này, bước triển khai hợp lý nhất là làm trước: khóa API rủi ro → migration schema P2P → message/WS contract, rồi mới đưa AI quay lại trên nền scope đúng.