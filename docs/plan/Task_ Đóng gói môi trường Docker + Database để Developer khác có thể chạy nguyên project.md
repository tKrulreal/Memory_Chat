# Task: Đóng gói môi trường Docker + Database để Developer khác có thể chạy nguyên project

## Mục tiêu

Project hiện tại của tôi đã chạy thành công trên máy local.

Tôi muốn:

1. Push toàn bộ code lên GitHub.
2. Developer khác chỉ cần `git pull`/`git clone`.
3. Cài Docker Desktop.
4. Chạy một vài command.
5. Docker tự khởi động toàn bộ project.
6. PostgreSQL chạy trong Docker.
7. PostgREST chạy trong Docker nếu project đang sử dụng.
8. Qdrant chạy trong Docker nếu project đang sử dụng.
9. Developer khác có thể sử dụng **cùng bộ dữ liệu development hiện tại của tôi**, không phải database trống.
10. Sau khi setup xong, project của developer khác phải hoạt động tương đương môi trường hiện tại của tôi.

---

# QUY TẮC AN TOÀN — CỰC KỲ QUAN TRỌNG

Trước khi thực hiện bất kỳ thao tác database nào:

- KHÔNG xóa PostgreSQL hiện tại trên máy tôi.
- KHÔNG reset database hiện tại.
- KHÔNG chạy `DROP DATABASE`.
- KHÔNG chạy `docker compose down -v` trên database hiện tại nếu chưa có backup.
- KHÔNG thay đổi dữ liệu production nếu project có production database.
- KHÔNG commit `.env`.
- KHÔNG commit password/secret/API key thật.
- KHÔNG commit dữ liệu nhạy cảm nếu phát hiện dữ liệu người dùng thật.

Database hiện tại phải được backup trước.

---

# PHASE 1 — Phân tích project hiện tại

Trước tiên hãy kiểm tra:

- Backend framework.
- Frontend framework.
- PostgreSQL configuration.
- PostgREST configuration.
- Qdrant configuration.
- Redis hoặc service phụ thuộc khác.
- Migration system.
- Seed system.
- Database schema.
- Database tables.
- Environment variables.
- Docker files hiện có.
- Docker Compose hiện có.
- Git repository structure.

Xác định chính xác project hiện tại có những service nào.

Không được giả định project chỉ có PostgreSQL.

Sau khi phân tích, đưa ra architecture hiện tại.

Ví dụ:

```text
Frontend
   ↓
Backend
   ├──→ PostgREST
   │       ↓
   │   PostgreSQL
   │
   └──→ Qdrant
```

---

# PHASE 2 — Thiết kế Docker architecture

Mục tiêu cuối cùng:

```text
Docker Compose
│
├── frontend
│
├── backend
│
├── postgrest
│
├── postgres
│
└── qdrant
```

Chỉ tạo service nếu project thực sự sử dụng service đó.

PostgreSQL phải dùng Docker volume.

Ví dụ:

```yaml
volumes:
  postgres_data:
```

Qdrant cũng phải sử dụng persistent volume nếu project cần giữ vector data:

```yaml
volumes:
  qdrant_data:
```

---

# PHASE 3 — Database hiện tại

Đây là phần quan trọng nhất.

Tôi muốn developer khác có thể nhận được **database development hiện tại** của tôi.

Trước tiên hãy xác định:

- PostgreSQL host.
- PostgreSQL port.
- Database name.
- Username.
- Schema.
- Tables.
- Extensions.
- Functions.
- Triggers.
- Indexes.
- Constraints.
- Current migration state.
- Các dữ liệu hiện tại cần giữ.

Sau đó tạo database backup bằng PostgreSQL native tools.

Ưu tiên sử dụng:

```bash
pg_dump
```

KHÔNG copy trực tiếp thư mục PostgreSQL data directory từ máy tôi sang repository.

Ưu tiên tạo backup dạng:

```text
database/
└── development.dump
```

hoặc phương án tương đương phù hợp với project.

---

# PHASE 4 — Quyết định cách lưu database dump

Sau khi kiểm tra dữ liệu, hãy xác định liệu database có chứa:

- user thật
- email thật
- password
- token
- API key
- personal information
- production data
- dữ liệu nhạy cảm

hay không.

### Nếu database chỉ chứa dữ liệu development/test

Có thể đưa database dump vào repository nếu kích thước hợp lý.

Ví dụ:

```text
database/
└── development.dump
```

### Nếu database chứa dữ liệu nhạy cảm

KHÔNG commit dump lên GitHub.

Thay vào đó:

1. Tạo sanitized development database.
2. Loại bỏ dữ liệu nhạy cảm.
3. Tạo dump từ sanitized database.
4. Hoặc cung cấp script download/restore từ một nơi an toàn.

Nếu dump quá lớn để Git lưu trữ bình thường, hãy đề xuất Git LFS hoặc một phương án artifact/storage phù hợp.

Không tự ý upload dữ liệu lên dịch vụ bên ngoài.

---

# PHASE 5 — PostgreSQL initialization

Docker PostgreSQL phải có cơ chế:

```text
docker compose up
        ↓
PostgreSQL container
        ↓
Database chưa tồn tại?
        ↓
Create database
        ↓
Restore development dump
        ↓
Database ready
```

Nếu PostgreSQL Docker image có cơ chế `/docker-entrypoint-initdb.d/`, có thể sử dụng phù hợp.

Tuy nhiên phải đảm bảo dump được restore đúng cách.

Không restore dump mỗi lần container restart.

Database chỉ được initialize khi volume/database mới.

---

# PHASE 6 — Migration và development dump

Phải phân biệt rõ:

```text
Migration
    =
Database schema/version
```

và:

```text
Development dump
    =
Schema + development data
```

Mục tiêu là developer mới có thể:

```text
clone repository
      ↓
docker compose up
      ↓
PostgreSQL
      ↓
development data restored
      ↓
PostgREST
      ↓
Backend
      ↓
Frontend
```

Nếu migration và dump có thể xung đột, phải xử lý rõ ràng.

Không chạy migration một cách mù quáng lên database dump nếu có nguy cơ làm hỏng dữ liệu.

Thiết kế một flow initialization deterministic.

---

# PHASE 7 — Qdrant

Nếu project sử dụng Qdrant:

Kiểm tra xem Qdrant hiện tại có dữ liệu vector quan trọng hay không.

Nếu vector database cũng cần được chia sẻ cho developer mới, phải xác định cách backup/restore phù hợp.

Mục tiêu:

```text
PostgreSQL
+
Qdrant
```

đều có dữ liệu development tương ứng nếu application cần chúng.

Nếu Qdrant có thể rebuild từ PostgreSQL bằng indexing/embedding pipeline, hãy ưu tiên cách rebuild deterministic thay vì commit dữ liệu Qdrant binary lớn vào Git.

Nếu không thể rebuild, hãy đưa ra phương án backup/restore rõ ràng.

---

# PHASE 8 — PostgREST

Nếu project đang sử dụng PostgREST, phải Dockerize nó.

PostgREST phải kết nối PostgreSQL bằng Docker service name.

Ví dụ:

```env
PGRST_DB_URI=postgres://postgres:password@postgres:5432/app
```

Không dùng:

```env
PGRST_DB_URI=postgres://postgres:password@localhost:5432/app
```

khi PostgREST chạy trong container.

PostgREST phải start sau PostgreSQL đã sẵn sàng.

---

# PHASE 9 — Environment configuration

Tạo:

```text
.env.example
```

Không commit `.env` thật.

`.env.example` phải có đầy đủ biến cần thiết để developer mới tạo `.env`.

Ví dụ:

```env
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432

PGRST_DB_URI=postgres://postgres:postgres@postgres:5432/app
PGRST_DB_SCHEMA=public

QDRANT_URL=http://qdrant:6333
```

Các secret thật phải được thay bằng placeholder.

Nếu backend/frontend có configuration khác, phải đưa vào `.env.example`.

---

# PHASE 10 — Docker Compose

Tạo hoặc cập nhật:

```text
docker-compose.yml
```

Docker Compose phải đảm bảo:

```text
postgres
   ↓
postgrest
   ↓
backend
   ↓
frontend
```

và:

```text
backend → qdrant
```

nếu cần.

PostgreSQL:

- persistent volume
- healthcheck
- environment configuration

Qdrant:

- persistent volume
- healthcheck nếu phù hợp

Backend:

- dependency đúng
- environment đúng

Frontend:

- API URL đúng với Docker architecture.

---

# PHASE 11 — One-command setup

Tôi muốn developer mới có workflow đơn giản nhất có thể.

Mục tiêu:

```bash
git clone <repository>
cd <repository>

cp .env.example .env

docker compose up --build
```

Sau đó project tự setup.

Nếu cần một bước initialization riêng thì tạo script:

```text
scripts/
└── setup.sh
```

hoặc:

```text
Makefile
```

hoặc phương án phù hợp với OS.

Vì developer có thể sử dụng Windows, ưu tiên workflow hoạt động được trên Windows + Docker Desktop.

Nếu cần command riêng cho Windows PowerShell, document nó.

---

# PHASE 12 — Database restore command

Ngoài automatic initialization, phải cung cấp cách restore database thủ công.

Ví dụ concept:

```bash
docker compose exec -T postgres pg_restore ...
```

hoặc command phù hợp với format dump thực tế.

README phải có:

```text
Initial setup
Database restore
Database backup
Database reset
```

---

# PHASE 13 — Backup

Tạo command để tôi có thể backup database development hiện tại.

Ví dụ:

```bash
docker compose exec postgres pg_dump ...
```

hoặc script:

```text
scripts/
├── backup-db
└── restore-db
```

Không được hard-code password trong script nếu có cách an toàn hơn.

---

# PHASE 14 — Git safety

Kiểm tra:

```bash
git status
```

Đảm bảo không commit:

```text
.env
.env.local
*.pem
*.key
credentials
secrets
node_modules
.venv
__pycache__
build
dist
```

Đặc biệt kiểm tra database dump trước khi commit.

Nếu database dump chứa dữ liệu nhạy cảm:

DỪNG và báo cho tôi.

Không tự động commit.

---

# PHASE 15 — Test như một developer hoàn toàn mới

Sau khi setup xong, phải test từ trạng thái sạch.

Giả lập:

```text
Developer mới
       ↓
git clone
       ↓
cp .env.example .env
       ↓
docker compose up --build
```

Kiểm tra:

### 1. PostgreSQL

```bash
docker compose ps
```

PostgreSQL phải healthy.

### 2. Database

Kiểm tra database tồn tại.

### 3. Development data

Kiểm tra một số bảng quan trọng.

Phải xác nhận dữ liệu development hiện tại đã được restore.

### 4. PostgREST

Kiểm tra PostgREST có thể query database.

### 5. Qdrant

Nếu sử dụng, kiểm tra Qdrant hoạt động.

### 6. Backend

Backend phải kết nối thành công tới:

```text
PostgreSQL/PostgREST
Qdrant
```

### 7. Frontend

Frontend phải kết nối được backend.

### 8. Restart

```bash
docker compose restart
```

Dữ liệu không được mất.

### 9. Recreate container

```bash
docker compose down
docker compose up -d
```

Dữ liệu vẫn phải còn.

### 10. Clean database initialization

Nếu test:

```bash
docker compose down -v
docker compose up --build
```

thì database phải có khả năng được tạo/restore lại theo đúng thiết kế.

Cảnh báo rõ rằng:

```bash
docker compose down -v
```

sẽ xóa Docker database volume.

---

# PHASE 16 — README hoàn chỉnh

Cập nhật README với một section:

# Docker Development Setup

Phải giải thích cho developer mới:

## Requirements

```text
Git
Docker Desktop
```

Không yêu cầu cài PostgreSQL/PostgREST/Qdrant local nếu chúng đã được Dockerize.

## First setup

```bash
git clone <repo>
cd <repo>
cp .env.example .env
docker compose up --build
```

## Services

Hiển thị bảng:

```text
Service       Port       Purpose
frontend      xxxx       Frontend
backend       xxxx       API
postgrest     xxxx       REST API
postgres      xxxx       Database
qdrant        xxxx       Vector DB
```

Chỉ liệt kê service thực tế của project.

## Database

Giải thích:

- Database được chạy bằng Docker.
- Database development dump nằm ở đâu.
- Khi nào dump được restore.
- Migration hoạt động như thế nào.
- Volume hoạt động như thế nào.

## Commands

```bash
docker compose up -d
docker compose up --build
docker compose down
docker compose restart
docker compose logs
docker compose logs -f
```

## Database backup

Document command.

## Database restore

Document command.

## Reset database

Document command và cảnh báo dữ liệu sẽ mất.

## Troubleshooting

Document:

- port conflict
- database connection refused
- PostgREST connection failure
- Qdrant unavailable
- migration failure
- frontend/backend connection failure
- Docker volume issue

---

# PHASE 17 — Final report

Sau khi hoàn thành, báo cáo cho tôi:

## 1. Architecture

```text
Frontend
   ↓
Backend
   ↓
PostgREST
   ↓
PostgreSQL

Backend
   ↓
Qdrant
```

hoặc architecture thực tế.

## 2. Files created

Liệt kê tất cả file.

## 3. Files modified

Liệt kê tất cả file.

## 4. Database strategy

Giải thích chính xác:

- Database hiện tại được backup như thế nào.
- Dump nằm ở đâu.
- Có commit dump lên GitHub hay không.
- Khi developer mới chạy Docker thì database được restore như thế nào.
- Migration được chạy khi nào.
- Qdrant data được xử lý thế nào.

## 5. Developer setup

Đưa đúng command mà bạn tôi cần chạy sau khi `git clone`.

Mục tiêu:

```bash
git clone <repo>
cd <repo>
cp .env.example .env
docker compose up --build
```

## 6. Verification

Liệt kê tất cả test đã chạy và kết quả.

## 7. Security check

Xác nhận:

- `.env` không được commit.
- Secret không được commit.
- Database dump đã được kiểm tra.
- Không có credential thật trong repository.

## 8. Remaining issues

Nếu còn bất kỳ vấn đề nào, phải nói rõ.

---

# FINAL REQUIREMENT

Tôi không muốn chỉ có Docker configuration.

Tôi muốn một workflow hoàn chỉnh:

```text
MÁY TÔI
PostgreSQL hiện tại
       │
       │ backup
       ▼
Development database dump
       │
       ▼
GitHub / safe artifact
       │
       │ git clone / pull
       ▼
MÁY BẠN
       │
       ▼
docker compose up
       │
       ├── PostgreSQL
       │       ↓
       │   restore data
       │
       ├── PostgREST
       │
       ├── Qdrant
       │
       ├── Backend
       │
       └── Frontend
       │
       ▼
Project chạy với dữ liệu development
```

Hãy ưu tiên phương án đơn giản, an toàn, reproducible và phù hợp với project hiện tại.

**Không được tự ý xóa hoặc reset database hiện tại của tôi.**

Bắt đầu bằng việc phân tích project và báo cáo architecture trước khi thực hiện thay đổi.