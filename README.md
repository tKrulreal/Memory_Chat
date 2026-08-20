# 🤖 MemoryChat — AI-Powered Messaging Platform

**MemoryChat** là nền tảng nhắn tin AI-native với khả năng ghi nhớ và hiểu mối quan hệ dài hạn với người dùng.

---

## 🐳 Docker Development Setup

> Developer mới chỉ cần Git + Docker Desktop — không cần cài Python, Node, PostgreSQL local.

### Requirements

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Quick Start

```bash
# 1. Clone và cd vào project
git clone <repository-url>
cd P-214

# 2. Copy và chỉnh sửa .env
cp .env.example .env
# Chỉnh sửa .env: OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, JWT_SECRET

# 3. Build và chạy
docker compose up --build
```

> ✅ **Tự động hoàn toàn**: Backend tự động chạy database migrations khi khởi động.

### Services

| Service  | Port | URL                          |
|----------|------|------------------------------|
| Frontend | 3000 | http://localhost:3000        |
| Backend | 8000 | http://localhost:8000        |
| API Docs | 8000 | http://localhost:8000/docs   |
| Postgres| 5432 | localhost:5432              |

> **Qdrant**: Sử dụng **Qdrant Cloud** (SaaS). Cấu hình trong `.env`:
> - `QDRANT_URL`
> - `QDRANT_API_KEY`
> - Đăng ký miễn phí tại [cloud.qdrant.io](https://cloud.qdrant.io)

### Everyday Commands

```bash
# Start background
docker compose up -d

# Rebuild và start
docker compose up --build

# Stop (giữ data)
docker compose down

# Restart
docker compose restart

# Xem logs
docker compose logs -f         # Tất cả
docker compose logs -f backend # Backend only

# Kiểm tra trạng thái
docker compose ps
```

### Database

Database PostgreSQL chạy hoàn toàn trong Docker:

- **Volume**: `pgdata` — data được giữ nguyên sau `docker compose down`
- **Migrations**: Tự động chạy khi backend khởi động
- **Development dump**: `database/development.sql` — được restore lần đầu tiên

```bash
# Backup database
make db-backup

# Update development.sql từ database hiện tại
make db-dump

# Restore từ backup
make db-restore FILE=backup/db-TIMESTAMP.sql

# Reset về development.sql
make db-reset
```

> ⚠️ **Cảnh báo**: `docker compose down -v` sẽ **XÓA** volume `pgdata` và toàn bộ data!

---

## ⚡ Local Development

### Backend ngoài Docker (với hot reload)

```bash
# Chỉ chạy database trong Docker
docker compose up -d postgres

# Chạy backend trực tiếp với hot reload
cd P-214
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
python -m uvicorn src.main:app --reload --port 8000
```

---

## 🔧 Troubleshooting

### Port đã được sử dụng

```bash
# Kiểm tra port
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Đổi port trong .env
POSTGRES_PORT=5433
```

### Backend không healthy

```bash
# Xem logs
docker compose logs backend

# Restart
docker compose restart backend
```

### Database migration lỗi

```bash
# Chạy migration thủ công
docker compose exec backend python -m alembic upgrade head

# Kiểm tra migrations hiện tại
docker compose exec backend python -m alembic history
```

### Reset hoàn toàn

```bash
docker compose down -v
docker compose up --build
```

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────┐
│              Frontend (Next.js :3000)            │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              Backend (FastAPI :8000)             │
├──────────────────────┬──────────────────────────┤
│                      │                          │
│      PostgreSQL      │     Qdrant Cloud        │
│     (:5432 Docker)   │   (Vector Store)        │
└──────────────────────┴──────────────────────────┘
```

Documentation:
- [System Architecture](docs/specs/architecture.md)
- [AI Agents](docs/specs/ai-agents.md)
- [Database Schema](docs/specs/database.md)
- [API Endpoints](docs/specs/api.md)

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI + Uvicorn |
| LLM | OpenAI `gpt-4o-mini` (LangGraph) |
| Agent | LangGraph Orchestrator |
| Database | PostgreSQL 15 (Docker) + Alembic |
| Vector DB | Qdrant Cloud |
| Frontend | Next.js + TypeScript |
| Container | Docker Compose |

---

## 🌍 Environment Variables

Xem [`.env.example`](.env.example) để biết tất cả biến cần thiết.

```bash
cp .env.example .env
# Bắt buộc:
# - OPENAI_API_KEY
# - QDRANT_URL
# - QDRANT_API_KEY
# - JWT_SECRET
```

---

## 📁 Project Structure

```
├── alembic/              # Database migrations
├── database/             # Development database dump
│   └── development.sql  # Auto-restored on first run
├── src/
│   ├── agents/          # LangGraph AI Agents
│   ├── api/v1/          # FastAPI Routers
│   ├── models/          # SQLAlchemy Models
│   ├── services/        # Business Logic & LLM Gateway
│   └── main.py          # Application Entrypoint
├── frontend/             # Next.js Frontend
├── scripts/              # Utility scripts
├── .env.example          # Environment Variables Template
├── Makefile              # Development commands
├── docker-compose.yml    # Docker services
└── RUN_WITH_DOCKER.md   # Docker setup guide
```

---

## 🎯 Features

- 💬 **Chat**: Real-time messaging với WebSocket
- 🧠 **AI Memory**: Tự động ghi nhớ thông tin về Contact
- 🔍 **Semantic Search**: Tìm kiếm theo ngữ nghĩa
- 🤖 **AI Copilot**: Trợ lý AI trả lời theo ngữ cảnh
- 💡 **Recommendations**: Đề xuất follow-up, reply, priority
- 🏷️ **Tags & Connections**: Tự động gợi ý tags và kết nối

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SPEC.md](docs/specs/SPEC.md) | Project specifications |
| [RUN_WITH_DOCKER.md](RUN_WITH_DOCKER.md) | Docker setup guide |
| [AI Agents](docs/specs/ai-agents.md) | AI agent architecture |
| [API](docs/specs/api.md) | API endpoints reference |
| [Frontend](docs/specs/frontend.md) | Frontend architecture |
