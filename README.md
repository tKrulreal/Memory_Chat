# 🤖 MemoryChat — AI-Powered Messaging Platform

**MemoryChat** là nền tảng nhắn tin AI-native với khả năng ghi nhớ và hiểu mối quan hệ dài hạn với người dùng.

## ⚡ Quick Start
```bash
# Clone và setup
git clone <repository-url>
cd P-214
cp .env.example .env
# Edit .env với OPENAI_API_KEY của bạn

# Chạy với Docker
make run

# Hoặc local development
make setup
make run
# Server chạy tại http://localhost:8000
```

## 🏗 Architecture
Documentation:
- [System Architecture](docs/specs/architecture.md)
- [AI Agents](docs/specs/ai-agents.md)
- [Database Schema](docs/specs/database.md)
- [API Endpoints](docs/specs/api.md)

## 🛠 Tech Stack (MVP)
| Layer | Technology |
|-------|-----------|
| API | FastAPI + Uvicorn |
| LLM | OpenAI `gpt-4o-mini` (LangGraph) |
| Agent | LangGraph Orchestrator |
| Database | SQLite (SQLAlchemy 2.0) |
| Vector DB | ChromaDB |
| Validation | Pydantic v2 |
| Frontend | React + Vite + TypeScript |
| Container | Docker |
| Dev Tool | Makefile, Alembic |

## 🌍 Environment Variables
Xem `.env.example` để biết các biến cần thiết. Copy sang `.env` và điền API key:
```bash
cp .env.example .env
# Edit .env với OPENAI_API_KEY
```
Key variables: `OPENAI_API_KEY`, `DATABASE_URL`, `JWT_SECRET`.

## 📦 Database Migration
Dùng Alembic cho database migrations:
```bash
# Chạy migrations
alembic upgrade head

# Tạo migration mới
alembic revision --autogenerate -m "description"

# Rollback
alembic downgrade -1
```

## 🧪 Running Tests
Dùng pytest cho unit và integration tests:
```bash
# Tất cả tests
make test

# Chỉ unit tests
pytest tests/unit/ -v

# Với coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## 📁 Project Structure
```
├── alembic/              # Database migrations
├── src/
│   ├── agents/          # LangGraph AI Agents (Memory, Search, Recommendation, Copilot)
│   ├── api/v1/          # FastAPI API Routers
│   ├── core/            # Core utilities (logging, middlewares, exceptions)
│   ├── events/          # Event Bus (async pub/sub)
│   ├── models/          # SQLAlchemy DB Models (11 tables)
│   ├── repositories/    # Database CRUD Repositories
│   ├── schemas/         # Pydantic Schemas
│   ├── services/        # Business Logic & LLM Gateway
│   ├── workers/         # Background Workers (Memory, Recommendation, Insight)
│   ├── ws/              # WebSocket Manager
│   ├── config.py        # App Configuration (Pydantic Settings)
│   └── main.py          # Application Entrypoint
├── frontend/            # React Frontend
├── tests/               # Unit & Integration Tests
├── scripts/             # Utility scripts (backup, restore, seed)
├── docs/                # Documentation
│   ├── specs/           # Technical specifications
│   └── plan/            # Workstream plans
├── .env.example         # Environment Variables Template
├── Makefile             # Development commands
└── docker-compose.yml    # Docker deployment
```

## 🎯 Features

- **💬 Chat**: Real-time messaging với WebSocket
- **🧠 AI Memory**: Tự động ghi nhớ thông tin về Contact
- **🔍 Semantic Search**: Tìm kiếm theo ngữ nghĩa
- **🤖 AI Copilot**: Trợ lý AI trả lời theo ngữ cảnh
- **💡 Recommendations**: Đề xuất follow-up, reply, priority
- **🏷️ Tags & Connections**: Tự động gợi ý tags và kết nối

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SPEC.md](docs/specs/SPEC.md) | Project specifications |
| [Architecture](docs/specs/architecture.md) | System architecture |
| [AI Agents](docs/specs/ai-agents.md) | AI agent architecture |
| [API](docs/specs/api.md) | API endpoints reference |
| [Frontend](docs/specs/frontend.md) | Frontend architecture |
