# 🤖 MemoryChat — AI-Native Messaging & Context-Aware Relationship Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Railway%20App-00c853?style=for-the-badge&logo=railway)](https://c4-app-214.up.railway.app/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%200.115+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2015-336791?style=for-the-badge&logo=postgresql)](https://www.postgresql.org)
[![LangGraph](https://img.shields.io/badge/AI%20Orchestrator-LangGraph-FF6F00?style=for-the-badge&logo=openai)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/Container-Docker%20Compose-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com)

> 🌐 **Live Production URL:** [https://c4-app-214.up.railway.app/](https://c4-app-214.up.railway.app/)

---

## 📖 Giới Thiệu (Overview)

**MemoryChat** là nền tảng nhắn tin P2P thế hệ mới tích hợp sâu các **AI Agents** (Multi-Agent System với LangGraph) giúp tự động trích xuất thông tin, ghi nhớ ngữ cảnh dài hạn (Long-term Memory), gợi ý kết nối mạng lưới thông minh (AI Matchmaker) và hỗ trợ trợ lý cá nhân **AI Copilot** theo ngữ cảnh riêng của từng người dùng.

### ✨ Tính Năng Nổi Bật (Key Features)

- 💬 **Real-time Chat & P2P Messaging:** Nhắn tin thời gian thực với WebSocket, hỗ trợ thả cảm xúc (emoji reactions), trả lời tin nhắn (reply thread), trạng thái đã đọc và đếm tin nhắn chưa đọc.
- 🧠 **AI Long-term Memory (Trí nhớ thông minh):** Tự động phân tích hội thoại theo cửa sổ trượt (Memory Window), trích xuất tóm tắt và sự thật (facts), quản lý linh hoạt qua AI Hub.
- 🤖 **AI Copilot Chat:** Trợ lý ảo hiểu rõ hồ sơ cá nhân và ngữ cảnh mối quan hệ của bạn, lưu trữ lịch sử nhiều lượt trò chuyện (multi-turn conversation) và cho phép quản lý lịch sử trò chuyện độc lập.
- 🤝 **Smart Connection & Matchmaker:** Thuật toán AI đối sánh 5 bước (Jaccard Similarity, Mục tiêu tương hỗ, Địa lý, Hoạt động) để đề xuất bạn bè phù hợp nhất.
- 👥 **Quản Lý Kết Nối & Lời Mời:** Gửi, Chấp nhận, Từ chối, Hủy lời mời kết bạn và Hủy kết bạn (Unfriend) đồng bộ tức thì trên cả trang Bạn bè và Trung tâm thông báo.
- 🔔 **Interactive Notification Center:** Thông báo phân loại rõ ràng (Chưa đọc / Đã đọc), cập nhật trạng thái tương tác tức thời (Đã chấp nhận / Đã từ chối).

---

## 🛠️ Tech Stack

| Thành phần | Công nghệ / Thư viện | Mục đích sử dụng |
|---|---|---|
| **Backend API** | **FastAPI** (Python 3.11), Uvicorn | RESTful API hiệu năng cao, WebSocket real-time |
| **AI Framework** | **LangGraph**, **LangChain**, OpenAI / OpenRouter | Xây dựng luồng Multi-Agent, Memory Agent, Recommendation Agent, Copilot Agent |
| **Primary Database** | **PostgreSQL 15**, SQLAlchemy 2.0, Alembic | Lưu trữ dữ liệu quan hệ, transactional outbox pattern, migration tự động |
| **Vector Database** | **Qdrant Cloud** | Lưu trữ vector embeddings phục vụ Semantic Search & Trí nhớ AI |
| **Frontend** | **Next.js 14** (App Router), TypeScript, React | Giao diện người dùng hiện đại, Server & Client Components |
| **Styling & UI** | **Tailwind CSS**, Radix UI, Lucide Icons, Sonner | Giao diện chuẩn mực, responsive, dark/light theme |
| **State & Cache** | **TanStack Query** (React Query), **Zustand** | Quản lý server state, optimistic updates và client store |
| **DevOps & Deploy** | **Docker**, Docker Compose, Railway | Đóng gói container, triển khai cloud production |

---

## 🏗️ Cấu Trúc Thư Mục (Project Structure)

```
P-214/
├── alembic/                      # Quản lý Database Migrations (13 revisions tuyến tính)
│   ├── versions/                 # Các file migration từ gốc đến HEAD
│   └── env.py                    # Cấu hình Alembic môi trường
├── docs/                         # Tài liệu kiến trúc và đặc tả kỹ thuật
│   ├── specs/                    # Đặc tả API, AI Agents, Database, Architecture
│   └── plan/                     # Kế hoạch phát triển chi tiết
├── frontend/                     # Mã nguồn Next.js Frontend
│   ├── app/                      # Next.js App Router (chats, connections, notifications, copilot, profile, settings)
│   ├── components/               # UI components (chat, ai, layout, modals, ui)
│   ├── lib/                      # API clients, stores (Zustand), hooks, utils
│   ├── types/                    # TypeScript interfaces & types
│   ├── Dockerfile                # Multi-stage Docker build cho Next.js Standalone
│   └── package.json              # Frontend dependencies
├── src/                          # Mã nguồn Backend FastAPI
│   ├── agents/                   # LangGraph AI Agents (Orchestrator, Memory, Connection, Reply, Search, Tagging)
│   ├── api/                      # REST API Routers (v1: auth, chat, connections, copilot, notifications, profile...)
│   ├── core/                     # Bảo mật, JWT, Middlewares, Structured Logging, Scheduler
│   ├── events/                   # Event Bus & Outbox Event types
│   ├── models/                   # SQLAlchemy Models (User, Chat, AI, Contact, Connection...)
│   ├── schemas/                  # Pydantic Schemas (Request/Response validation)
│   ├── services/                 # Business logic & LLM Gateway
│   ├── workers/                  # Background Workers (Outbox Worker, Memory Worker)
│   └── main.py                   # Application Entrypoint & Lifespan
├── tests/                        # Toàn bộ Test Suite (81 Unit & Integration Tests với Pytest)
├── .env.example                  # File cấu hình biến môi trường mẫu
├── .gitignore                    # Bộ quy tắc bỏ qua file nhạy cảm, logs, cache
├── docker-compose.yml            # Khởi chạy toàn bộ hệ thống (Frontend + Backend + PostgreSQL)
├── Dockerfile                    # Multi-stage Docker build cho Backend FastAPI
├── requirements.txt              # Danh sách Python dependencies (pinned versions)
├── seed_data.py                  # Script nạp dữ liệu mẫu chuẩn (Users, Profiles, AI Context, Chats)
└── README.md                     # Tài liệu hướng dẫn dự án
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy (Step-by-Step Guide)

### Cách 1: Chạy bằng Docker (Khuyên Dùng — Nhanh & Tiện Lợi Nhất)

> **Yêu cầu:** Máy đã cài đặt [Git](https://git-scm.com/) và [Docker Desktop](https://www.docker.com/products/docker-desktop/).

#### Bước 1: Clone Repository
```bash
git clone <repository-url>
cd P-214
```

#### Bước 2: Thiết Lập Biến Môi Trường
Tạo file `.env` từ file mẫu `.env.example`:
```bash
cp .env.example .env
```
*Cấu hình các API key cần thiết trong file `.env` (ví dụ: `OPENAI_API_KEY`, `JWT_SECRET`).*

#### Bước 3: Khởi Động Toàn Bộ Ứng Dụng Với Docker Compose
```bash
docker compose up -d --build
```
> ✅ **Tự động hóa:** Container backend sẽ **tự động chạy lệnh `alembic upgrade head`** để tạo mới và cập nhật toàn bộ database schema lên phiên bản mới nhất.

#### Bước 4: Nạp Dữ Liệu Mẫu (Seed Data)
Chạy lệnh sau để nạp ngay 5 tài khoản mẫu và dữ liệu hội thoại, trí nhớ AI:
```bash
docker compose exec backend python seed_data.py
```

#### Bước 5: Truy Cập Ứng Dụng
- **Frontend App:** [http://localhost:3000](http://localhost:3000)
- **Backend API Docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Database PostgreSQL:** `localhost:5432`

---

### Cách 2: Chạy Thủ Công Trên Môi Trường Local

#### 1. Khởi chạy Database:
```bash
docker compose up -d postgres
```

#### 2. Cài đặt và chạy Backend:
```bash
# Tạo virtual environment
python -m venv .venv
source .venv/bin/activate   # Trên Linux/macOS
# .venv\Scripts\activate   # Trên Windows

# Cài đặt thư viện
pip install -r requirements.txt

# Chạy migration
alembic upgrade head

# Nạp dữ liệu mẫu
python seed_data.py

# Khởi chạy server FastAPI
uvicorn src.main:app --reload --port 8000
```

#### 3. Cài đặt và chạy Frontend:
```bash
cd frontend
npm install
npm run dev
```
Truy cập giao diện tại: `http://localhost:3000`

---

## 👥 Danh Sách Tài Khoản Mẫu Để Trải Nghiệm (Test Accounts)

Tất cả các tài khoản đều có mật khẩu mặc định là: `password123`

| Họ và tên | Email | Vai trò / Nghề nghiệp | Điểm mạnh hồ sơ AI |
|---|---|---|---|
| **Trần Minh** | `minh.tran@example.com` | Senior Backend Engineer | Python, FastAPI, Docker, Microservices |
| **Nguyễn Thị Lan** | `lan.nguyen@example.com` | Lead Product Manager | EdTech, SaaS Growth, Design Thinking |
| **Phạm Khoa** | `khoa.pham@example.com` | AI & Data Scientist | RAG Pipelines, LLM Agents, PyTorch |
| **Lê Mai** | `mai.le@example.com` | Senior Frontend Developer | Next.js, React Native, UI/UX Design |
| **Võ Hiếu** | `hieu.vo@example.com` | DevOps & Cloud Architect | Kubernetes, AWS, CI/CD, Terraform |

---

## 🌍 Danh Sách Biến Môi Trường Cần Thiết (Environment Variables)

| Tên Biến | Mô Tả | Ví Dụ Định Dạng / Giá Trị Mẫu | Bắt Buộc |
|---|---|---|:---:|
| `APP_ENV` | Môi trường triển khai | `development` / `production` | Không |
| `DEBUG` | Chế độ debug | `true` / `false` | Không |
| `APP_PORT` | Port backend lắng nghe | `8000` | Không |
| `DATABASE_URL` | Chuỗi kết nối PostgreSQL | `postgresql://user:pass@host:5432/dbname` | **Có** |
| `JWT_SECRET` | Khóa bí mật mã hóa token JWT | `chuỗi_bí_mật_ngẫu_nhiên` | **Có** |
| `JWT_EXPIRE_MINUTES` | Thời gian hết hạn của Access Token | `60` | Không |
| `OPENAI_API_KEY` | API Key OpenAI cho các AI Agents | `sk-proj-...` | **Có** |
| `USE_OPENROUTER` | Bật sử dụng OpenRouter thay cho OpenAI | `false` / `true` | Không |
| `OPENROUTER_API_KEY` | API Key OpenRouter (nếu bật) | `sk-or-...` | Không |
| `QDRANT_URL` | URL kết nối Vector DB Qdrant Cloud | `https://xxxx.aws.cloud.qdrant.io` | Tùy chọn |
| `QDRANT_API_KEY` | API Key xác thực Qdrant Cloud | `xxxx...` | Tùy chọn |
| `NEXT_PUBLIC_API_URL`| URL Backend API cung cấp cho Frontend | `http://localhost:8000` | **Có** |

---

## 📡 Tài Liệu API Chính (Key API Endpoints)

Hệ thống cung cấp đầy đủ Swagger UI tương tác tại `/docs`. Dưới đây là tóm tắt các endpoint chính:

### 1. Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/register`: Đăng ký tài khoản mới.
- `POST /api/v1/auth/login`: Đăng nhập, nhận JWT Access Token.
- `GET /api/v1/auth/me`: Lấy thông tin user hiện tại.

### 2. Conversations & Real-time Messages (`/api/v1/conversations`)
- `GET /api/v1/conversations`: Danh sách cuộc trò chuyện trực tiếp (kèm unread count, last message).
- `POST /api/v1/conversations`: Tạo hoặc mở cuộc trò chuyện với bạn bè.
- `GET /api/v1/conversations/{id}/messages`: Phân trang lịch sử tin nhắn.
- `POST /api/v1/conversations/{id}/read`: Đánh dấu đã đọc toàn bộ tin nhắn trong hội thoại.
- `WS /api/v1/ws/chat`: Kênh WebSocket real-time nhận gửi tin nhắn và reaction.

### 3. Connection Requests & Network (`/api/v1/connection-requests`)
- `GET /api/v1/connection-requests`: Danh sách lời mời (incoming, outgoing, pending).
- `POST /api/v1/connection-requests`: Gửi lời mời kết bạn mới.
- `POST /api/v1/connection-requests/{id}/accept`: Chấp nhận kết bạn (tự động tạo cuộc trò chuyện).
- `POST /api/v1/connection-requests/{id}/reject`: Từ chối lời mời kết bạn.
- `POST /api/v1/connection-requests/{id}/cancel`: Thu hồi lời mời kết bạn đã gửi.
- `DELETE /api/v1/connection-requests/friends/{target_user_id}`: Hủy kết bạn (Unfriend) an toàn.

### 4. AI Copilot & Memory Hub (`/api/v1/copilot` & `/api/v1/assistant`)
- `POST /api/v1/copilot/chat`: Trò chuyện với AI Copilot có ngữ cảnh quan hệ và profile.
- `GET /api/v1/copilot/messages`: Lấy lịch sử chat Copilot theo cài đặt Memory Window.
- `DELETE /api/v1/copilot/messages`: Xóa lịch sử chat Copilot.
- `POST /api/v1/assistant/context/refresh`: Làm mới và trích xuất lại AI Memory & Relationship Context.

### 5. Notifications & Profile (`/api/v1/notifications` & `/api/v1/profile`)
- `GET /api/v1/notifications`: Lấy danh sách thông báo (phân trang).
- `POST /api/v1/notifications/{id}/read`: Đánh dấu đã đọc một thông báo.
- `POST /api/v1/notifications/read-all`: Đánh dấu đã đọc toàn bộ thông báo.
- `GET /api/v1/profile/me`: Lấy hồ sơ cá nhân và cài đặt AI Hub.
- `PUT /api/v1/profile/me`: Cập nhật thông tin profile và tùy chọn AI.

---

## 🧪 Kiểm Thử (Testing)

Dự án tuân thủ nghiêm ngặt chuẩn mực **Test-Driven Development (TDD)** với 100% test cases tự động:

```bash
# Chạy toàn bộ 81 bài kiểm thử
pytest tests/ -v
```

**Kết quả kiểm thử:**
```text
======================= 81 passed, 1 warning in 18.12s ========================
```

---

## 👨‍💻 Thành Viên Dự Án (Team Members)

| Họ và tên | Vai trò | Trách nhiệm chính |
|---|---|---|
| **Đội ngũ Phát triển P-214** | **Fullstack & AI Engineers** | Kiến trúc Multi-Agent, Backend FastAPI, Frontend Next.js, DevOps & Deployment |

---

## 🔗 Liên Kết Quan Trọng (Important Links)

- 🚀 **Live Production:** [https://c4-app-214.up.railway.app/](https://c4-app-214.up.railway.app/)
- 📑 **Swagger API Docs:** [https://c4-app-214.up.railway.app/docs](https://c4-app-214.up.railway.app/docs)
