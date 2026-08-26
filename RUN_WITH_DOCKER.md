# 🐳 Chạy MemoryChat với Docker

## Cách sử dụng đơn giản nhất

### 1. Pull code về
```bash
git clone <repo-url>
cd P-214
```

### 2. Cài đặt `.env`
```bash
# Nếu chưa có .env, copy từ .env.example
cp .env.example .env

# Chỉnh sửa .env với API key của bạn
# Các giá trị quan trọng cần có:
# - OPENAI_API_KEY
# - DATABASE_URL (đã có sẵn cho Docker)
# - QDRANT_URL và QDRANT_API_KEY (Qdrant Cloud)
```

### 3. Build và chạy
```bash
docker-compose up --build
```

> ✅ **Tự động chạy migrations**: Backend sẽ tự động chạy `alembic upgrade head` khi khởi động.

### 4. Truy cập
| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

## Cấu trúc Services

```
┌─────────────────────────────────────────────────┐
│              docker-compose                      │
├─────────────────────────────────────────────────┤
│  postgres:5432  │  Database PostgreSQL          │
│  backend:8000   │  FastAPI Backend             │
│  frontend:3000  │  Next.js Frontend            │
│  Qdrant Cloud   │  Vector Store (external)     │
└─────────────────────────────────────────────────┘
```

> **Lưu ý**: Project sử dụng **Qdrant Cloud** cho vector storage (đã cấu hình trong `.env`).

## Các lệnh hữu ích

### Chạy background
```bash
docker-compose up --build -d
```

### Xem logs
```bash
# Tất cả services
docker-compose logs -f

# Chỉ backend
docker-compose logs -f backend

# Chỉ postgres
docker-compose logs -f postgres
```

### Restart
```bash
docker-compose restart
```

### Stop
```bash
docker-compose down
```

### Reset hoàn toàn (xóa database)
```bash
docker-compose down -v
docker-compose up --build
```

### Rebuild không cache
```bash
docker-compose build --no-cache
```

## Troubleshooting

### Lỗi port đã được sử dụng
```bash
# Kiểm tra port đang dùng
netstat -ano | findstr :8000
netstat -ano | findstr :5432
netstat -ano | findstr :3000
```

### Backend không healthy
```bash
# Xem logs backend
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Database migration lỗi
```bash
# Chạy migration thủ công
docker exec p-214-backend-1 python -m alembic upgrade head

# Hoặc xem chi tiết
docker-compose logs backend | grep -A5 "alembic"
```

## Environment Variables quan trọng

File `.env` cần có các biến sau:

```env
# Database (PostgreSQL trong Docker)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/memorychat

# LLM
OPENAI_API_KEY=sk-...          # Required

# Vector Store (Qdrant Cloud)
QDRANT_URL=https://xxx.qdrant.io
QDRANT_API_KEY=your-qdrant-key

# Auth
JWT_SECRET=your-secret-key
```

## Development

### Chạy backend ngoài Docker (với hot reload)
```bash
# Chỉ chạy postgres trong Docker
docker-compose up -d postgres

# Chạy backend trực tiếp với hot reload
cd P-214
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
python -m uvicorn src.main:app --reload --port 8000
```
