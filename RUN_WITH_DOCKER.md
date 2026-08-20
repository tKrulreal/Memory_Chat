# 🐳 Chạy MemoryChat với Docker

## Cách sử dụng đơn giản nhất

### 1. Pull code về
```bash
git clone <repo-url>
cd P-214
```

### 2. Tạo file .env (hoặc dùng .env có sẵn)
```bash
# Đã có .env rồi thì bỏ qua bước này
cp .env.example .env
# Rồi chỉnh sửa .env với API key của bạn
```

### 3. Build và chạy
```bash
docker-compose up --build
```

### 4. Truy cập
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## Các lệnh hữu ích

### Chạy background (khuyến nghị)
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

### Xóa hoàn toàn (reset)
```bash
docker-compose down -v
```

### Rebuild không cache
```bash
docker-compose build --no-cache
```

## Cấu trúc services

```
┌─────────────────────────────────────────────────┐
│              docker-compose                      │
├─────────────────────────────────────────────────┤
│  postgres:5432  │  Database (local)           │
│  backend:8000   │  FastAPI Backend             │
│  frontend:3000  │  Next.js Frontend            │
│  Qdrant Cloud   │  Vector Store (external)     │
└─────────────────────────────────────────────────┘
```

> **Lưu ý**: Qdrant đang dùng **Qdrant Cloud** (đã có trong `.env`), không cần chạy local.

## Troubleshooting

### Lỗi port đã được sử dụng
```bash
# Kiểm tra port đang dùng
netstat -ano | findstr :8000
netstat -ano | findstr :5432
netstat -ano | findstr :3000

# Hoặc đổi port trong docker-compose.yml
```

### Lỗi "Module not found"
```bash
# Rebuild lại image
docker-compose build --no-cache backend
```

### Lỗi database connection
```bash
# Kiểm tra postgres đã healthy chưa
docker-compose ps

# Reset database
docker-compose down -v
docker-compose up -d postgres
# Đợi 10s rồi chạy tiếp
docker-compose up -d
```

### Xem logs chi tiết
```bash
docker-compose logs --tail=100 backend
```

## Environment Variables quan trọng

Trong file `.env`:

```env
# Database - dùng Docker
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/memorychat

# Khi chạy trong Docker, QDRANT_URL phải là tên service
# QDRANT_URL=http://qdrant:6333  # trong docker-compose

# Qdrant Cloud (nếu dùng external)
QDRANT_URL=https://xxx.qdrant.io
QDRANT_API_KEY=your-key

# LLM
OPENAI_API_KEY=sk-...
```

## Development với Docker

### Hot reload cho backend
Backend đã có volumes mount code, nhưng uvicorn trong Docker mặc định không hot reload.

Để enable hot reload, sửa Dockerfile hoặc chạy trực tiếp:

```bash
# Sửa CMD trong Dockerfile thành:
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

Hoặc chạy backend ngoài Docker, chỉ dùng Docker cho postgres + qdrant:
```bash
# Chỉ chạy database
docker-compose up -d postgres qdrant

# Rồi chạy backend bình thường
python -m uvicorn src.main:app --reload
```
