# 🤖 AI20K Agent Backend

This is the backend for the AI20K Project.

## ⚡ Quick Start
```bash
git clone https://github.com/AI20K-Build-Cohort-2/starter-code-template.git
cd projectAi
make setup
make run
```

## 🏗 Architecture
Please refer to the detailed architecture documentation:
- [Backend Architecture](docs/general overview/05_Backend_Architecture.md)

## 🛠 Tech Stack (MVP)
- **Backend Framework**: FastAPI + Uvicorn
- **AI/LLM**: LangGraph, LangChain, OpenAI GPT-4o-mini
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **ORM**: SQLAlchemy + Alembic
- **Testing**: pytest

## 🌍 Environment Variables
Please refer to the `.env.example` file for the required environment variables. You must copy it to `.env` and fill in your keys:
```bash
cp .env.example .env
```
Key variables include `OPENAI_API_KEY`, `DATABASE_URL`, and `JWT_SECRET`.

## 📦 Database Migration
We use Alembic for database migrations. To initialize or upgrade your schema to the latest version:
```bash
alembic upgrade head
```

## 🧪 Running Tests
We use pytest for unit and integration testing. Run tests using:
```bash
python -m pytest tests/unit/ -v
```

## 📁 Project Structure
```
├── alembic/              # Database migrations
├── src/
│   ├── agents/           # LangGraph Agent logic
│   ├── api/v1/           # FastAPI Routers
│   ├── models/           # SQLAlchemy DB Models
│   ├── repositories/     # Database CRUD Repositories
│   ├── services/         # Business Logic & LLM Gateway
│   ├── config.py         # App Configuration
│   └── main.py           # Application Entrypoint
├── tests/                # Unit Tests
└── .env.example          # Environment Variables Template
```
