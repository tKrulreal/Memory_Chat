# Development Journal — MemoryChat

> Nhật ký phát triển. Ghi lại mỗi tuần: quyết định kỹ thuật, khó khăn, bài học.

---

## Week 1: 2026-07-25

### Mục tiêu tuần
- [x] Xác định đúng vấn đề và điểm đau cốt lõi của người dùng
- [x] Giới hạn phạm vi MVP
- [x] Xác định các tính năng tạo nên giá trị khác biệt

### Đã hoàn thành
- Initial project commit với FastAPI backend và React frontend

### Quyết định kỹ thuật & Lý do
| Quyết định | Lý do | Kết quả |
|------------|-------|---------|
| Chọn P2P messaging thay vì group chat | Tập trung vào core value là AI memory cho relationships | MVP rõ ràng hơn |
| Dùng LangGraph cho AI orchestration | State machine phù hợp với multi-agent flows | Code dễ maintain hơn |

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| Xác định điểm khác biệt với Zalo/WhatsApp | Tập trung vào AI Memory và Copilot | Sản phẩm có USP rõ ràng |

### Bài học rút ra
- Chọn đúng điểm đau là quyết định quan trọng nhất

---

## Week 2: 2026-08-05 to 2026-08-06

### Mục tiêu tuần
- [x] Xây dựng nền tảng backend và cơ sở dữ liệu
- [x] Hoàn thiện xác thực và phân quyền cơ bản

### Đã hoàn thành
- Database models, repositories, services
- Authentication với JWT security
- LLM Gateway integration

### Quyết định kỹ thuật & Lý do
| Quyết định | Lý do | Kết quả |
|------------|-------|---------|
| Dùng FastAPI thay vì Flask | Native async, Pydantic validation, Swagger auto-generated | Developer experience tốt hơn |
| JWT access token | Stateless, scalable, dễ integrate với mobile | Phù hợp với architecture |
| SQLAlchemy 2.0 + Alembic | Type-safe, async support, migration management | Database management dễ hơn |

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| Nhiều người code song song, schema khác nhau | Chuẩn hóa Pydantic schemas, review code | Các component ghép được với nhau |
| CORS và UUID serialization | Thêm middleware, convert UUID ở layer boundary | API hoạt động ổn định |

### Bài học rút ra
- Contract rõ ràng quan trọng hơn code nhanh

---

## Week 3: 2026-08-07 to 2026-08-15

### Mục tiêu tuần
- [x] Xây dựng bộ nhớ dài hạn từ hội thoại
- [x] Triển khai semantic search và lưu trữ vector
- [x] Bảo vệ dữ liệu riêng tư và giới hạn ngữ cảnh AI

### Đã hoàn thành
- Memory Agent trích xuất facts và summaries
- Vector store với ChromaDB (sau chuyển sang Qdrant)
- Transactional Outbox pattern cho async processing

### Quyết định kỹ thuật & Lý do
| Quyết định | Lý do | Kết quả |
|------------|-------|---------|
| Memory Window (cửa sổ thời gian) | Không phải lịch sử nào cũng còn liên quan | Giảm noise, tăng relevance |
| Phân vùng vector theo owner_user_id | Semantic search không được trả về memories của người khác | Privacy được đảm bảo ở tầng vector |
| Chuyển từ ChromaDB sang Qdrant Cloud | ChromaDB local không phù hợp với deployment cloud | Vector search ổn định hơn |

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| ChromaDB không phù hợp production | Migrate sang Qdrant Cloud | Ổn định hơn |
| Prompt injection và data leak | Thêm guardrails layer | Bảo mật hơn |

### Bài học rút ra
- Semantic search chỉ đáng tin khi phân vùng privacy được enforce

---

## Week 4: 2026-08-16 to 2026-08-20

### Mục tiêu tuần
- [x] Xây dựng Copilot và các AI Agent chuyên biệt
- [x] Kết nối Agent với dữ liệu hồ sơ, tin nhắn và bộ nhớ
- [x] Tăng độ ổn định của quá trình gọi công cụ và sinh phản hồi

### Đã hoàn thành
- Orchestrator Agent với intent classification
- Memory, Search, Matchmaker, Reply, Tagging Agents
- Copilot chat với multi-turn context

### Quyết định kỹ thuật & Lý do
| Quyết định | Lý do | Kết quả |
|------------|-------|---------|
| LangGraph `bind_tools` thay vì LangGraph full | Đủ cho MVP, tránh over-engineering | Code đơn giản hơn |
| Giới hạn context theo user/conversation | Không leak data, giảm token usage | Secure và cost-effective |

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| Tool returns empty data | Thêm validation và fallback | Copilot vẫn respond được |
| Prompt injection attempts | Guardrails với keyword detection | Security improved |

### Bài học rút ra
- Bắt đầu simple, scale khi cần

---

## Week 5: 2026-08-21 to 2026-08-27

### Mục tiêu tuần
- [x] Hoàn thiện frontend và real-time features
- [x] Triển khai Docker và CI/CD

### Đã hoàn thành
- Modern chat UI với presence và read receipts
- Real-time notifications
- Docker Compose setup
- GitHub Actions CI pipeline

### Quyết định kỹ thuật & Lý do
| Quyết định | Lý do | Kết quả |
|------------|-------|---------|
| WebSocket cho real-time | Real-time requirement cao | Instant message delivery |
| Docker Compose orchestration | Reproducible deployment | Dev team productivity tăng |
| Multi-stage Docker build | Giảm image size | Deploy nhanh hơn |

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| WebSocket reconnection | Exponential backoff | Reconnect reliably |
| CI/CD race conditions | Proper health checks | Stable pipeline |

### Bài học rút ra
- Real-time features cần careful state management

---

## Week 6: 2026-08-28 to 2026-09-04

### Mục tiêu tuần
- [x] Hoàn thiện AI features và guardrails
- [x] Chuẩn bị deliverables cho Demo Day
- [x] Fix bugs và polish

### Đã hoàn thành
- In-Chat Copilot isolation per conversation
- Comprehensive guardrails cho Copilot
- Password reset functionality
- Documentation và deliverables

### Quyết định kỹ thuật & Lý do
| Quyết định | Lý do | Kết quả |
|------------|-------|---------|
| Copilot isolation theo conversation | Mỗi hội thoại có context riêng | Relevant responses |
| Guardrails layer | Ngăn prompt injection và data leak | Security hardened |
| Separate AI Hub settings | User control over AI behavior | Better UX |

### Khó khăn & Giải pháp
| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| AI Memory không detect conflict | Cần similarity check | Issue logged, pending fix |
| Empty responses from LLM | Fallback response + error handling | Graceful degradation |

### Bài học rút ra
- Security và UX cần được test với real users

---

## Tổng Kết Các Quyết Định Quan Trọng

| Quyết định | Lý do | Kết quả |
|------------|-------|---------|
| P2P thay vì Group Chat | Focus vào AI Memory | Clear USP |
| FastAPI + LangGraph | Developer experience | Fast iteration |
| Qdrant Cloud thay ChromaDB | Production-ready | Stable deployment |
| JWT authentication | Stateless | Scalable |
| WebSocket real-time | UX requirement | Instant delivery |
| Docker + CI/CD | Reproducibility | Team productivity |

---

## ✅ Checklist Trước Khi Submit

- [x] Có ít nhất 6 entries (1 per week)
- [x] Mỗi entry có 2-3 câu mô tả
- [x] Đã ghi quyết định kỹ thuật quan trọng
- [x] Đã ghi bài học rút ra
