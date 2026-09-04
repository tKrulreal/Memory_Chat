# Nhật Ký Phát Triển - MemoryChat

> Nhật ký ghi lại các quyết định kỹ thuật, khó khăn, giải pháp và bài học chính trong quá trình phát triển MemoryChat.

---

## Tuần 1: 25/07/2026 - 04/08/2026

### Mục tiêu tuần
- [x] Xác định đúng vấn đề và điểm đau cốt lõi của người dùng
- [x] Giới hạn phạm vi MVP
- [x] Xác định các tính năng tạo nên giá trị khác biệt của MemoryChat

### Đã hoàn thành
- Thu hẹp bài toán từ việc xây dựng một ứng dụng nhắn tin có nhiều tính năng thành giải quyết một điểm đau cụ thể: hội thoại chứa nhiều thông tin quan trọng về con người, cam kết và sở thích chung, nhưng người dùng phải tự ghi nhớ và tìm lại chúng.
- Xác định phạm vi MVP gồm nhắn tin P2P, bộ nhớ dài hạn, tìm kiếm theo ngữ cảnh, AI Copilot và đề xuất kết nối.

### Quyết định kỹ thuật & Lý do
| Quyết định | Lý do | Kết quả |
|------------|-------|---------|
| Tập trung vào khả năng ghi nhớ và khai thác ngữ cảnh hội thoại | Đây là điểm đau rõ ràng mà các ứng dụng nhắn tin thông thường chưa giải quyết tốt | Các tính năng AI đều phục vụ trực tiếp cho việc ghi nhớ, tìm kiếm và cải thiện mối quan hệ |
| Giới hạn MVP ở hội thoại trực tiếp giữa hai người | Tránh dàn trải nguồn lực vào nhóm chat và các tính năng nhắn tin không tạo khác biệt | Phạm vi dự án rõ ràng và có thể hoàn thành trong thời gian cho phép |

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| Ý tưởng ban đầu có phạm vi rộng và dễ trở thành một ứng dụng chat thông thường | Đánh giá lại nhu cầu cốt lõi và loại bỏ các tính năng không trực tiếp giải quyết điểm đau | Hình thành định hướng sản phẩm nhất quán cho toàn bộ dự án |

### Bài học rút ra
- Lựa chọn đúng điểm đau là quyết định quan trọng nhất vì nó chi phối toàn bộ sản phẩm và kiến trúc; giải tốt một vấn đề không cần thiết vẫn có thể khiến dự án thất bại.

---

## Tuần 2: 05/08/2026 - 06/08/2026

### Mục tiêu tuần
- [x] Xây dựng nền tảng backend và cơ sở dữ liệu
- [x] Hoàn thiện xác thực và phân quyền cơ bản
- [x] Thống nhất cách tích hợp các phần backend do nhiều thành viên phát triển

### Đã hoàn thành
- Xây dựng backend bằng FastAPI, PostgreSQL, SQLAlchemy và Alembic; triển khai JWT, mô hình dữ liệu, repository, service và LLM Gateway.
- Thiết lập mô hình hội thoại P2P, REST API cho các thao tác ghi dữ liệu, WebSocket cho sự kiện thời gian thực và Transactional Outbox kết hợp EventBus cho tác vụ nền.

### Quyết định kỹ thuật & Lý do
| Quyết định | Lý do | Kết quả |
|------------|-------|---------|
| Sử dụng kiến trúc backend và xác thực theo hướng truyền thống | MVP cần đơn giản, quen thuộc, dễ kiểm thử nhưng vẫn hoạt động đầy đủ | Nền tảng ổn định để các tính năng AI và giao diện tiếp tục phát triển |
| Dùng REST cho yêu cầu từ client và WebSocket cho sự kiện từ server | REST cung cấp validation, JWT và mã lỗi rõ ràng; WebSocket chỉ đảm nhiệm đồng bộ thời gian thực | Giảm độ phức tạp của giao thức và dễ xử lý lỗi hơn |
| Ghi sự kiện vào Transactional Outbox trước khi EventBus xử lý | Tránh mất tác vụ AI hoặc xử lý dữ liệu chưa được commit | Đảm bảo tác vụ nền không chặn luồng gửi tin nhắn và có thể được xử lý lại |

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| Các thành viên phát triển model, repository, service và API song song nên xuất hiện khác biệt về schema, chữ ký sự kiện và kiểu dữ liệu | Chuẩn hóa contract, Pydantic schema, UUID và ranh giới giữa router, service và worker | Các thành phần backend có thể ghép lại và hoạt động thống nhất |
| Phát sinh lỗi CORS, tuần tự hóa UUID, ownership và nguy cơ ghi log PII | Sửa middleware, bổ sung kiểm tra quyền sở hữu và che dữ liệu nhạy cảm trong log | Backend an toàn và phù hợp hơn cho tích hợp frontend |

### Bài học rút ra
- Với MVP có nhiều người cùng phát triển, kiến trúc quen thuộc và contract rõ ràng có giá trị hơn việc đưa vào các thành phần phức tạp quá sớm.

---

## Tuần 3: 07/08/2026 - 15/08/2026

### Mục tiêu tuần
- [x] Xây dựng bộ nhớ dài hạn từ hội thoại
- [x] Triển khai semantic search và lưu trữ vector
- [x] Bảo vệ dữ liệu riêng tư và giới hạn ngữ cảnh AI

### Đã hoàn thành
- Memory Agent trích xuất bản tóm tắt, sở thích, việc cần theo dõi, dòng thời gian và tín hiệu về mức độ quan hệ từ hội thoại.
- Xây dựng Memory Worker để xử lý nền, tạo embedding và lưu bộ nhớ vào vector store; sau đó chuyển từ ChromaDB cục bộ sang Qdrant Cloud để phù hợp hơn với môi trường triển khai.
- Bổ sung cửa sổ thời gian bộ nhớ và bộ lọc bắt buộc theo `owner_user_id`, đồng thời có thể giới hạn theo `conversation_id` khi truy xuất.

### Quyết định kỹ thuật & Lý do
| Quyết định | Lý do | Kết quả |
|------------|-------|---------|
| Lưu các thông tin bền vững và hữu ích, ngoại trừ thông tin nhạy cảm, nội dung prompt injection và dữ liệu ít giá trị | Dữ liệu không phù hợp có thể làm lộ thông tin hoặc khiến mô hình đi lệch khỏi yêu cầu | Bộ nhớ cô đọng và an toàn hơn cho các tác vụ AI |
| Cho phép người dùng cấu hình thời hạn ngữ cảnh | Toàn bộ lịch sử không phải lúc nào cũng còn liên quan và có thể làm tăng nhiễu | Chỉ những tin nhắn nằm trong khoảng thời gian phù hợp được đưa vào quá trình xây dựng ngữ cảnh |
| Bắt buộc phân vùng vector theo chủ sở hữu | Semantic search không được phép trả về bộ nhớ của người dùng khác | Ngăn truy xuất chéo người dùng ngay tại tầng vector store |

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| Vector store cục bộ không phù hợp với môi trường cloud và khó duy trì dữ liệu ổn định khi triển khai | Chuyển sang Qdrant Cloud và tạo payload index cho chủ sở hữu, hội thoại và memory ID | Tìm kiếm vector hoạt động ổn định hơn trong production |
| Ngữ cảnh quá cũ hoặc nội dung nguy hiểm có thể làm giảm chất lượng câu trả lời | Áp dụng memory window, kiểm tra dữ liệu nhạy cảm và phát hiện prompt injection | Kết quả AI bám sát dữ liệu liên quan hơn |

### Bài học rút ra
- Semantic search chỉ đáng tin cậy khi việc chọn lọc bộ nhớ, tính gần đây, phân vùng riêng tư và grounding theo dữ liệu của đúng người dùng được xem là yêu cầu cốt lõi.

---

## Tuần 4: 16/08/2026 - 20/08/2026

### Mục tiêu tuần
- [x] Xây dựng Copilot và các AI Agent chuyên biệt
- [x] Kết nối Agent với dữ liệu hồ sơ, tin nhắn và bộ nhớ
- [x] Tăng độ ổn định của quá trình gọi công cụ và sinh phản hồi

### Đã hoàn thành
- Xây dựng các Agent cho memory, search, connection matching, tagging, insight và reply suggestion, sau đó cung cấp các khả năng phù hợp cho Copilot dưới dạng tool.
- Copilot sử dụng hồ sơ, tin nhắn gần đây, bộ nhớ semantic và lịch sử nhiều lượt để trả lời theo ngữ cảnh; In-Chat Copilot được cô lập theo từng cuộc hội thoại.

### Quyết định kỹ thuật & Lý do
| Quyết định | Lý do | Kết quả |
|------------|-------|---------|
| Sử dụng LangChain `bind_tools` với vòng lặp gọi công cụ có kiểm soát thay cho state machine LangGraph đầy đủ | LangGraph tạo thêm độ phức tạp không cần thiết cho luồng Copilot của MVP | Luồng xử lý dễ theo dõi, kiểm thử và sửa lỗi hơn |
| Giới hạn dữ liệu và công cụ theo người dùng hoặc cuộc hội thoại hiện tại | Copilot không được phép sử dụng dữ liệu ngoài phạm vi yêu cầu | Giảm nguy cơ rò rỉ dữ liệu và trả lời sai ngữ cảnh |

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| Tool orchestration đôi khi trả về dữ liệu rỗng, sai định dạng hoặc phản hồi không có nội dung | Bổ sung validation, fallback và xử lý phản hồi rỗng | Copilot vẫn trả về kết quả rõ ràng khi LLM hoặc tool gặp lỗi |
| Copilot có nguy cơ bịa thông tin, nhận prompt injection hoặc truy cập sai hội thoại | Thêm system prompt chặt chẽ, ownership check, guardrail và phân vùng context | Hành vi của Agent ổn định và an toàn hơn |

### Bài học rút ra
- Độ tin cậy của Agent đến từ tool bị giới hạn, context đúng phạm vi, validation xác định và fallback rõ ràng hơn là từ việc tăng mức độ tự chủ của mô hình.

---

## Tuần 5: 21/08/2026 - 29/08/2026

### Mục tiêu tuần
- [x] Xây dựng AI Hub và hệ thống tagging
- [x] Cho phép người dùng cấu hình hành vi AI
- [x] Đồng bộ recommendation với thông báo và hành động kết nối

### Đã hoàn thành
- Xây dựng AI Hub để người dùng quản lý tag, bật hoặc tắt AI, cho phép đọc hồ sơ và trích xuất hội thoại, chọn memory window, số lượt context Copilot, chu kỳ recommendation và điểm matching tối thiểu.
- Hoàn thiện tagging tự động theo danh sách tag do người dùng định nghĩa, luồng duyệt hoặc từ chối tag, cùng hệ thống matchmaker và thông báo kết nối.

### Quyết định kỹ thuật & Lý do
| Quyết định | Lý do | Kết quả |
|------------|-------|---------|
| Agent chỉ được chọn tag từ danh sách do người dùng tạo | Việc tự sinh tag không kiểm soát làm kết quả khó hiểu và giảm niềm tin | Tag nhất quán với cách người dùng tổ chức các mối quan hệ |
| Cho phép cấu hình ngưỡng điểm và chu kỳ recommendation | Nhu cầu nhận đề xuất và mức độ phù hợp mong muốn khác nhau giữa các người dùng | Người dùng kiểm soát được tần suất và chất lượng gợi ý |
| Yêu cầu hành động chấp nhận hoặc từ chối đối với đề xuất quan trọng | AI nên hỗ trợ quyết định thay vì tự quyết định thay người dùng | Các tính năng AI minh bạch và có khả năng kiểm soát |

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| Kết quả Agent, dữ liệu đã lưu, ngưỡng cấu hình, notification và UI từng hiển thị trạng thái không đồng nhất | Áp dụng cùng cấu hình tại backend và đồng bộ trạng thái giữa recommendation card, notification và friend request | Kết quả matching và hành động kết nối nhất quán trên toàn ứng dụng |

### Bài học rút ra
- AI trở nên hữu ích và đáng tin hơn khi người dùng có thể đặt ranh giới, hiểu lý do xuất hiện của kết quả và chủ động chấp nhận hoặc từ chối đề xuất.

---

## Tuần 6: 16/08/2026 - 02/09/2026

### Mục tiêu tuần
- [x] Tích hợp frontend với REST API và WebSocket
- [x] Hoàn thiện các luồng chat, Copilot, kết nối, thông báo và cài đặt
- [x] Kiểm thử luồng người dùng đầu cuối

### Đã hoàn thành
- Kết nối frontend Next.js với các REST client có type, WebSocket sử dụng ticket xác thực, TanStack Query cho server state và Zustand cho client state.
- Đồng bộ tin nhắn, presence, read receipt, notification, Copilot và connection state theo thời gian thực; hoàn thiện giao diện chat, AI Hub, cài đặt và quản lý kết nối.

### Quyết định kỹ thuật & Lý do
| Quyết định | Lý do | Kết quả |
|------------|-------|---------|
| Tách REST client vào `frontend/lib/api/` và cập nhật cache khi nhận WebSocket event | Cần một nguồn dữ liệu thống nhất và tránh gọi lại toàn bộ API sau mỗi sự kiện | Giao diện phản hồi nhanh hơn và logic tích hợp dễ quản lý hơn |
| Dùng optimistic update cho các thao tác phù hợp | Người dùng cần thấy phản hồi ngay khi gửi tin nhắn hoặc thực hiện hành động | Trải nghiệm nhanh nhưng vẫn được đối chiếu với dữ liệu chính thức từ server |

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| API route, schema, UUID và trạng thái UI không khớp giữa frontend và backend | Chuẩn hóa type, response contract và các API client | Giảm lỗi 422, 500 và lỗi render dữ liệu |
| Optimistic update tạo tin nhắn trùng, notification bị cũ và Copilot dùng nhầm context giữa các hội thoại | Đối chiếu `client_message_id`, cập nhật đúng query cache và phân vùng lịch sử Copilot theo `conversation_id` | Luồng chat và AI hoạt động nhất quán hơn từ đầu đến cuối |

### Bài học rút ra
- Một tính năng chỉ hoàn thành khi authentication, persistence, real-time update, error state và toàn bộ hành trình người dùng cùng tuân theo một contract, không phải khi frontend và backend chỉ chạy tốt riêng lẻ.

---

## Tuần 7: 19/08/2026 - 04/09/2026

### Mục tiêu tuần
- [x] Đóng gói và triển khai ứng dụng ổn định
- [x] Xây dựng CI/CD và health check
- [x] Bổ sung observability và hardening trước khi demo

### Đã hoàn thành
- Container hóa backend, frontend và PostgreSQL bằng Docker, sử dụng multi-stage build, dependency health check, phiên bản thư viện production cố định và tự động chạy Alembic migration khi khởi động.
- Triển khai trên Railway, xây dựng CI/CD, liveness và readiness probe, Prometheus metrics, structured log có request ID và LangSmith tracing để theo dõi hoạt động của hệ thống và mô hình AI.

### Quyết định kỹ thuật & Lý do
| Quyết định | Lý do | Kết quả |
|------------|-------|---------|
| Sử dụng Docker cho môi trường development và deployment | Ứng dụng phải chạy nhất quán bên ngoài máy của lập trình viên | Giảm khác biệt môi trường và tăng khả năng tái tạo bản triển khai |
| Chọn Railway thay vì Vercel cho backend | Railway là lựa chọn kinh tế, quen thuộc, dễ sử dụng và phù hợp hơn với backend AI có tiến trình dài, WebSocket và PostgreSQL | Có môi trường production đơn giản để vận hành và trình diễn |
| Dùng LangSmith cùng structured log, Prometheus và health probe | Cần quan sát cả lỗi ứng dụng lẫn chất lượng và luồng thực thi AI | Dễ truy vết request, phát hiện dependency lỗi và kiểm tra hoạt động của mô hình |

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| Docker build và migration từng hoạt động không nhất quán giữa local và production | Tối ưu Dockerfile, cố định dependency, tự động migration và kiểm tra readiness | Quá trình khởi động và triển khai có thể lặp lại đáng tin cậy hơn |
| Log AI, secret, PII và lỗi model chưa đủ an toàn hoặc dễ quan sát | Bổ sung che dữ liệu nhạy cảm, request ID, guardrail, rate limit, request-size limit và sửa hệ thống AI log | Hệ thống an toàn hơn và dễ chẩn đoán trước buổi demo |

### Bài học rút ra
- Một buổi demo thành công không chỉ phụ thuộc vào số lượng tính năng mà còn phụ thuộc vào khả năng triển khai lặp lại, quan sát lỗi và xác nhận hệ thống đang hoạt động đúng.

---

## Checklist Trước Khi Submit

- [x] Có ít nhất 5-7 entries
- [x] Mỗi entry mô tả quyết định, khó khăn, giải pháp và bài học
- [x] Đã ghi các quyết định kỹ thuật quan trọng
- [x] Đã ghi bài học rút ra
