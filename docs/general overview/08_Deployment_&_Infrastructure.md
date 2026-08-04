# 08_Deployment_&_Infrastructure.md

# Deployment & Infrastructure

Project: MemoryChat

Version: MVP v1.0

---

# 1. Overview

Trong giai đoạn MVP, MemoryChat được triển khai theo mô hình **single-container Monolith** nhằm tối ưu cho hackathon 6 tuần và giảm chi phí vận hành.

Toàn bộ Backend (FastAPI + LangGraph + OpenAI client) chạy trong một container duy nhất. SQLite và ChromaDB được mount ra persistent volume để giữ dữ liệu qua các lần restart.

Mặc dù triển khai dưới dạng Monolith đơn giản, kiến trúc vẫn được thiết kế theo hướng **Module-first** và **Event-driven** để có thể tách thành Microservices trong tương lai mà không cần thay đổi Business Logic (xem [05_Backend_Architecture.md](05_Backend_Architecture.md)).

---

# 2. Deployment Goals

- Triển khai được trong thời gian 6 tuần.
- Chi phí thấp — tận dụng free tier của cloud.
- Dễ demo — 1 lệnh `make run` là chạy được.
- Dễ thay đổi LLM Provider.
- AI xử lý bất đồng bộ.
- Có khả năng triển khai bằng Docker.

---

# 3. MVP Infrastructure Overview

```
                    Internet
                        │
                  Reverse Proxy (Nginx/Caddy - tuỳ chọn)
                        │
                FastAPI Application (single container)
                        │
            ┌───────────┴───────────┐
            │                       │
        REST API               LangGraph Agent
            │                       │
            │                  OpenAI API
            │
       SQLite + ChromaDB (mounted volume)
```

Trong MVP không có:

- Redis.
- PostgreSQL (SQLite thay thế).
- Neo4j.
- Qdrant (ChromaDB thay thế).
- Celery Worker (in-process asyncio task thay thế).
- Nhiều service riêng biệt.

Toàn bộ gói gọn trong 1 Docker container.

---

# 4. Client Architecture

MVP hiện không có Frontend. Client dự kiến (sau MVP):

- React (Web).
- hoặc Flutter (Mobile).

Client giao tiếp với Backend thông qua:

- **REST API** cho Authentication, Contact, Search, Recommendation, AI Copilot.
- **WebSocket** cho Chat, Notification, AI Streaming (sau MVP).

Trong MVP, có thể test API qua:

- Swagger UI (`/docs`).
- curl / Postman.
- Frontend test (khi có).

---

# 5. Backend Deployment

Backend triển khai bằng FastAPI, chạy bằng Uvicorn trong Docker.

Hiện tại không dùng Gunicorn + nhiều Uvicorn Worker — chỉ chạy 1 process Uvicorn đơn giản để demo. Khi scale sẽ chuyển sang Gunicorn + multi-worker.

Không sử dụng Flask do khả năng Async kém hơn.

---

# 6. Reverse Proxy

Trong MVP không bắt buộc, nhưng khi triển khai production nên dùng Nginx/Caddy để:

- HTTPS.
- Reverse Proxy.
- Compression.
- Rate Limiting.
- Static File serving (sau này).

Nginx là điểm vào duy nhất của toàn bộ hệ thống (khi có).

---

# 7. AI Deployment

LLM không được host nội bộ trong MVP.

Hệ thống sử dụng **OpenAI API** thông qua LangChain `ChatOpenAI`.

Provider trong MVP:

- OpenAI `gpt-4o-mini` (qua biến `MODEL_NAME` trong `.env`).

Sau MVP có thể thay bằng:

- Anthropic Claude.
- Google Gemini.
- Local LLM (Llama 3, Qwen, DeepSeek, Mistral) thông qua Ollama hoặc vLLM.

Việc thay đổi Provider chỉ cần đăng ký trong LLM Gateway — không ảnh hưởng Agent.

---

# 8. AI Infrastructure

Trong MVP, AI Layer chạy in-process trong cùng container:

```
Assistant Orchestrator (LangGraph)
  ↓
AI Context Builder
  ↓
Prompt Builder
  ↓
Tool Registry
  ↓
AI Agents
  ↓
LLM (OpenAI)
  ↓
Response Validator
  ↓
Client
```

Sau MVP sẽ tách thành service riêng nếu cần.

---

# 9. Background Tasks

Trong MVP không có Celery. Background task được implement bằng `asyncio.create_task` chạy trong cùng process FastAPI:

- Memory Refresh (khi conversation idle).
- Embedding Update (sau khi Memory thay đổi).
- Recommendation Generation (sau Memory Update).

Sau MVP sẽ tách thành Celery Worker riêng với Redis làm Broker.

---

# 10. Event Bus

Trong MVP, Event Bus đơn giản hoá:

- Event ghi vào bảng `EventLog` (SQLite).
- Một asyncio loop đọc Event mới và xử lý.

Sau MVP sẽ thay bằng Redis Stream / Kafka.

---

# 11. Storage Architecture (MVP)

```
SQLite (./data/app.db)
  ↓
Business Data

ChromaDB (./data/chroma)
  ↓
Embedding
```

Mỗi loại dữ liệu được lưu đúng nơi phù hợp.

Khi scale:

- SQLite → PostgreSQL.
- ChromaDB → Qdrant.
- Bổ sung Redis (cache, session).
- Bổ sung Neo4j (knowledge graph).

---

# 12. Docker Architecture (MVP)

`docker-compose.yml` MVP chỉ có 1 service:

```yaml
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    env_file:
      - .env
```

Volume `./data` được mount để giữ:

- `app.db` (SQLite).
- `chroma/` (ChromaDB persist).

Sau MVP sẽ bổ sung thêm service: postgres, neo4j, qdrant, redis, worker-memory, worker-recommendation, worker-embedding.

---

# 13. Environment Variables

Các thông tin nhạy cảm được lưu trong file `.env` (xem `.env.example`).

Ví dụ:

```
OPENAI_API_KEY=
MODEL_NAME=gpt-4o-mini
DATABASE_URL=sqlite:///./data/app.db
CHROMA_PERSIST_DIR=./data/chroma
LOG_LEVEL=INFO
```

Không hard-code API Key trong mã nguồn.

---

# 14. Monitoring

Trong MVP theo dõi qua log:

- API Log (stdout container).
- AI Log (prompt + response, lưu `.ai-log/`).
- Error Log.

Sau MVP sẽ thêm:

- Prometheus.
- Grafana.
- OpenTelemetry tracing.
- Worker Queue Monitoring.

---

# 15. Logging

Chia thành nhiều loại log:

- Application Log.
- API Log.
- AI Log.
- Prompt Log (sau MVP).
- Error Log.

Mỗi Request có Request ID để truy vết.

---

# 16. Security

### MVP

- HTTPS (do reverse proxy đảm nhiệnh, khi deploy).
- Input Validation (Pydantic).
- Không commit API Key vào git.

### Sau MVP

- JWT Authentication.
- Password Hash (BCrypt).
- Authorization Middleware.
- Rate Limiting.
- Prompt Injection Detection.
- Output Validation.
- Context Isolation.

---

# 17. Cost Optimization

Hệ thống áp dụng các chiến lược sau:

### Không gọi LLM sau mỗi tin nhắn

Memory được cập nhật theo Event (idle, close, 20 messages, batch).

### Cache Context

Trong MVP lưu in-memory; sau MVP dùng Redis.

### Context Compression

Chỉ gửi Context cần thiết, không gửi toàn bộ Conversation.

### Batch Processing

Summary, Recommendation, Insight chạy nền (asyncio task trong MVP).

### Embedding Incremental

Chỉ tạo Embedding cho dữ liệu mới.

### Chọn model nhỏ

`gpt-4o-mini` cho tác vụ không cần lý luận sâu.

---

# 18. Scalability

Khi số lượng người dùng tăng:

| Thành phần | Scale |
|------------|-------|
| FastAPI | Horizontal (nhiều instance + Nginx) |
| Worker | Horizontal (Celery + Redis) |
| SQLite → PostgreSQL | Read replica, partitioning |
| ChromaDB → Qdrant | Cluster |
| Neo4j (mới) | Cluster |
| LLM | Đổi Provider hoặc Self-host |

Không cần thay đổi Business Logic.

---

# 19. Disaster Recovery

### MVP

- Backup volume `./data/` (SQLite + ChromaDB).

### Sau MVP

- Backup PostgreSQL.
- Backup Neo4j.
- Snapshot Qdrant.
- Redis không cần backup.

Có thể phục hồi từ Database chính.

---

# 20. CI/CD

Đề xuất sử dụng GitHub Actions.

Workflow mẫu:

```
Developer Push
  ↓
Run Test
  ↓
Build Docker Image
  ↓
Deploy
  ↓
Health Check
  ↓
Notify Team
```

Trong MVP, CI/CD chưa bắt buộc — chỉ cần `make run` local + deploy thủ công.

---

# 21. Production Readiness Checklist (MVP)

✅ Docker

✅ Environment Variables

✅ Logging

✅ Error Handling

✅ Health Check Endpoint

✅ Volume Persist cho SQLite + ChromaDB

⬜ HTTPS (do hosting provider)

⬜ JWT Authentication

⬜ Rate Limiting

⬜ Monitoring (Prometheus/Grafana)

⬜ CI/CD

---

# 22. Future Infrastructure

Sau MVP có thể mở rộng:

- Kubernetes.
- API Gateway riêng.
- Kafka thay Redis Stream.
- MCP Server.
- Multi-LLM Routing.
- Self-hosted LLM.
- Object Storage (MinIO/S3) cho media.
- CDN cho media.
- Multi-region deployment.

---

# 23. Infrastructure Principles

- MVP ưu tiên đơn giản: 1 container, 1 process, 1 SQLite, 1 ChromaDB.
- Event-driven thay vì đồng bộ (kể cả khi dùng in-memory queue).
- AI chạy nền, không chặn API.
- Mỗi thành phần có trách nhiệm rõ ràng.
- Có thể thay thế từng công nghệ mà không ảnh hưởng toàn hệ thống.
- Chi phí thấp nhưng vẫn sẵn sàng mở rộng.