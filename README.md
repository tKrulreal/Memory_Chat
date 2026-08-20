# 🤖 MemoryChat — AI-Powered Messaging Platform

**MemoryChat** là nền tảng nhắn tin AI-native với khả năng ghi nhớ và hiểu mối quan hệ dài hạn với người dùng.

---

## 🐳 Docker Development Setup

> Developer mới chỉ cần Git + Docker Desktop — không cần cài Python, Node, PostgreSQL local.

### Requirements

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### First Setup

```bash
git clone <repository-url>
cd P-214

# 1. Copy env file và điền API keys
cp .env.example .env
# Bắt buộc điền: OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, JWT_SECRET

# 2. Khởi động tất cả services
docker compose up --build
```

> **Lần đầu chạy**: PostgreSQL tự động restore từ `database/development.sql` — có sẵn development data.

### Services

| Service  | Port | Purpose                          |
|----------|------|----------------------------------|
| frontend | 3000 | Next.js UI → http://localhost:3000 |
| backend  | 8000 | FastAPI API → http://localhost:8000 |
| postgres | 5432 | PostgreSQL Database              |

> **Qdrant**: Cloud SaaS — cần cung cấp `QDRANT_URL` và `QDRANT_API_KEY` trong `.env`.  
> Đăng ký miễn phí tại [cloud.qdrant.io](https://cloud.qdrant.io).

### Everyday Commands

```bash
docker compose up -d          # Start background
docker compose up --build     # Rebuild images và start
docker compose down           # Stop (giữ data)
docker compose restart        # Restart services
docker compose logs -f        # Follow logs
docker compose logs backend   # Logs của service cụ thể
docker compose ps             # Xem trạng thái containers
```

### Database

Database PostgreSQL chạy hoàn toàn trong Docker:

- **Development dump**: `database/development.sql` — được restore tự động lần đầu
- **Volume**: `pgdata` — data được giữ nguyên sau `docker compose down`
- **Migration**: Alembic — chạy `make migrate` sau khi containers up

```bash
# Backup database hiện tại
make db-backup                    # → backup/db-TIMESTAMP.sql

# Update development.sql từ database hiện tại
make db-dump                      # → database/development.sql (overwrite)

# Restore từ backup cụ thể
make db-restore FILE=backup/db-20240820-120000.sql

# ⚠️ DANGER: Reset về development.sql
make db-reset
```

> **⚠️ WARNING**: `docker compose down -v` sẽ **XÓA** Docker volume `pgdata` và toàn bộ data!  
> Luôn backup trước: `make db-backup`

### Troubleshooting

<details>
<summary>Port 5432 already in use</summary>

Máy bạn đang có PostgreSQL local đang chạy port 5432. Giải pháp:

```bash
# Option 1: Đổi port trong .env
POSTGRES_PORT=5433

# Option 2: Dừng PostgreSQL local
# macOS: brew services stop postgresql
# Linux: sudo systemctl stop postgresql
```
</details>

<details>
<summary>Database connection refused / backend không start</summary>

```bash
# Kiểm tra postgres có healthy không
docker compose ps

# Xem logs postgres
docker compose logs postgres

# Nếu postgres không healthy, restart
docker compose restart postgres
```
</details>

<details>
<summary>Frontend không gọi được backend API</summary>

Kiểm tra `NEXT_PUBLIC_API_URL` trong `.env`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Rebuild frontend sau khi thay đổi:
```bash
docker compose up --build frontend
```
</details>

<details>
<summary>Qdrant connection error</summary>

Kiểm tra `QDRANT_URL` và `QDRANT_API_KEY` trong `.env`.  
Qdrant là Cloud SaaS — cần internet access và API key hợp lệ.
</details>

<details>
<summary>Reset toàn bộ và start lại từ đầu</summary>

```bash
# ⚠️ Xóa tất cả: containers, images, volumes
docker compose down -v
docker compose up --build
# PostgreSQL sẽ restore từ database/development.sql
```
</details>

---

## ⚡ Quick Start (Local Development)

```bash
cp .env.example .env
# Edit .env
docker compose up --build
```

## 🏗 Architecture

```text
Frontend (Next.js :3000)
        ↓
Backend (FastAPI :8000)
        ├──→ PostgreSQL (Docker :5432)
        └──→ Qdrant Cloud (SaaS external)
```

Documentation:
- [System Architecture](docs/specs/architecture.md)
- [AI Agents](docs/specs/ai-agents.md)
- [Database Schema](docs/specs/database.md)
- [API Endpoints](docs/specs/api.md)

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI + Uvicorn |
| LLM | OpenAI `gpt-4o-mini` (LangGraph) |
| Agent | LangGraph Orchestrator |
| Database | PostgreSQL 15 (Docker) + Alembic |
| Vector DB | Qdrant Cloud |
| Validation | Pydantic v2 |
| Frontend | Next.js + TypeScript |
| Container | Docker Compose |
| Dev Tool | Makefile |

## 🌍 Environment Variables

Xem [`.env.example`](.env.example) để biết tất cả biến cần thiết.

```bash
cp .env.example .env
# Bắt buộc: OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, JWT_SECRET
```

## 📦 Database Migrations

```bash
# Chạy migrations (sau khi docker compose up)
make migrate

# Tạo migration mới
make migrate-create MSG="add column"

# Rollback
docker compose exec backend alembic downgrade -1
```

## 🧪 Running Tests

```bash
make test           # All tests
make test-cov       # With coverage report
```

## 📁 Project Structure

```
├── alembic/              # Database migrations
├── database/             # Development database dump
│   └── development.sql   # Auto-restored on first Docker run
├── src/
│   ├── agents/          # LangGraph AI Agents
│   ├── api/v1/          # FastAPI Routers
│   ├── models/          # SQLAlchemy Models
│   ├── services/        # Business Logic & LLM Gateway
│   └── main.py          # Application Entrypoint
├── frontend/            # Next.js Frontend
├── scripts/             # Utility scripts
│   ├── backup-db.sh     # Backup PostgreSQL (bash)
│   ├── backup-db.ps1    # Backup PostgreSQL (PowerShell)
│   ├── restore-db.sh    # Restore PostgreSQL (bash)
│   └── restore-db.ps1   # Restore PostgreSQL (PowerShell)
├── .env.example         # Environment Variables Template
├── Makefile             # Development commands
└── docker-compose.yml   # Docker services
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
