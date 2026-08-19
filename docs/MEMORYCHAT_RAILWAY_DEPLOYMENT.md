# Hướng Dẫn Triển Khai MemoryChat Trên Railway

Tài liệu này là cẩm nang vận hành chính thức để triển khai ứng dụng MemoryChat lên nền tảng Railway. Tài liệu tuân thủ nghiêm ngặt các quy tắc và kiến trúc đã được định nghĩa trong `MEMORYCHAT_RAILWAY_DEPLOYMENT_PLAN.md`.

## 1. Tổng Quan Kiến Trúc Trên Railway

MemoryChat yêu cầu một kiến trúc gồm nhiều Service độc lập trên Railway:

1. **PostgreSQL Service**: Database được quản lý tự động (Managed database) dùng để lưu trữ dữ liệu quan hệ (Tin nhắn, User, Connection...).
2. **Backend Service (FastAPI)**: Chịu trách nhiệm xử lý REST APIs, WebSockets, các tác vụ AI ngầm (background workers), và ChromaDB.
3. **Frontend Service (Next.js)**: Chịu trách nhiệm hiển thị giao diện người dùng (UI).

```text
                    🌐 Internet
                         │
                    HTTPS / WSS
                         │
                         ▼
                  ┌──────────────┐
                  │   Railway    │
                  │              │
                  │  Next.js     │
                  │  FastAPI     │
                  │  PostgreSQL  │
                  └──────┬───────┘
                         │
                     Volume (ChromaDB)
```

---

## 2. Cài Đặt PostgreSQL (Phase 5)

1. Tạo một **New Project** (Dự án mới) trên Railway.
2. Click **Add a Plugin** (Thêm Plugin) -> **PostgreSQL**.
3. Railway sẽ tự động khởi tạo một cơ sở dữ liệu Postgres và cung cấp các biến môi trường nội bộ (ví dụ: `DATABASE_URL`).

---

## 3. Triển Khai Backend (Phases 2, 4, 6, 9)

### A. Tạo Service
1. Trong Project Railway của bạn, click **New** -> **GitHub Repo**.
2. Chọn kho lưu trữ `MemoryChat` của bạn.
3. Tại phần **Settings -> General**, đặt **Root Directory** (Thư mục gốc) là `/` (mặc định).

### B. Lưu Trữ Dữ Liệu Bền Vững (Persistent Storage - ChromaDB)
Bởi vì ChromaDB lưu trữ dữ liệu vector AI dưới dạng file local, bạn BẮT BUỘC phải gắn một Volume (ổ cứng) để dữ liệu không bị mất mỗi khi deploy lại.
1. Vào **Settings -> Volumes**.
2. Click **New Volume**.
3. Đặt **Mount Path** (Đường dẫn gắn) là `/app/data`.

### C. Biến Môi Trường (Secrets)
Vào tab **Variables** của Backend service và thêm các biến sau:

| Variable | Bí mật | Giá Trị / Mục Đích |
|---|---|---|
| `DATABASE_URL` | Có | *Sử dụng biến Reference của Railway: `${{Postgres.DATABASE_URL}}`* |
| `JWT_SECRET` | Có | *Tạo một chuỗi ngẫu nhiên, dài và bảo mật* |
| `OPENAI_API_KEY` | Có | *API Key của OpenAI (hoặc OpenRouter)* |
| `APP_ENV` | Không | `production` |
| `CORS_ORIGINS` | Không | `https://ten-mien-frontend-cua-ban.up.railway.app` |

*(Lưu ý: Không bao giờ commit các biến bí mật này lên Git).*

### D. Lệnh Khởi Chạy (Start Command)
Railway sẽ tự động cấp một cổng (`$PORT`) ngẫu nhiên. Bạn phải ghi đè lệnh chạy `uvicorn` mặc định để ứng dụng lắng nghe đúng cổng này.
1. Vào **Settings -> Deploy**.
2. Thiết lập **Custom Start Command**:
   `uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1`

### E. Chạy Migration Database (Khởi tạo bảng)
Ngay sau khi backend deploy thành công, bạn phải chạy lệnh tạo bảng cho Database.
1. Vào tab **Deployments** -> **View Logs**.
2. Mở tab **Terminal** của Backend service.
3. Chạy lệnh: `alembic upgrade head`
4. Kiểm tra trong PostgreSQL Data (Mục Data ở góc trên trang Railway) xem các bảng đã được tạo thành công chưa.

---

## 4. Triển Khai Frontend (Phases 2, 4, 8)

### A. Tạo Service
1. Click **New** -> **GitHub Repo**.
2. Chọn kho lưu trữ `MemoryChat` của bạn một lần nữa.
3. Tại phần **Settings -> General**, đặt **Root Directory** (Thư mục gốc) là `/frontend`.
*(Railway sẽ tự động nhận diện file `frontend/Dockerfile` và tiến hành build).*

### B. Biến Môi Trường
Vào tab **Variables** của Frontend service và thêm:

| Variable | Bí mật | Giá Trị / Mục Đích |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Không | `https://<ten-mien-backend-cua-ban>/api/v1` |
| `NEXT_PUBLIC_WS_URL` | Không | `wss://<ten-mien-backend-cua-ban>/ws` |

*KHÔNG ĐƯỢC để JWT_SECRET hay OPENAI_API_KEY ở Frontend.*

### C. Lệnh Khởi Chạy
File `frontend/Dockerfile` đã xuất sẵn biến `ENV PORT=3000` và dùng lệnh `node server.js`. Railway sẽ tự động ghi đè biến `$PORT` lúc chạy (runtime) nên bạn không cần cài đặt Custom Start Command cho Frontend.

---

## 5. Cấu Hình Tên Miền (Domain) (Phase 10)

1. Đối với cả Backend và Frontend, vào **Settings -> Networking**.
2. Click **Generate Domain** để lấy một tên miền miễn phí `.up.railway.app`, HOẶC click **Custom Domain** để trỏ tên miền riêng của bạn.
3. Đảm bảo rằng biến `CORS_ORIGINS` của Backend phải khớp chính xác với Domain của Frontend, và các biến `NEXT_PUBLIC_*` của Frontend phải trỏ đúng vào Domain của Backend.

---

## 6. Staging và Production (Phases 11 & 12)

Đừng vội vã đưa bản deploy đầu tiên cho người dùng cuối (Production).
1. Tạo một Environment trong Railway và đặt tên là **Staging**.
2. Triển khai cả Frontend và Backend lên Staging.
3. Chạy các bài test thủ công theo file [SMOKE_TESTING.md](./SMOKE_TESTING.md).
4. Chỉ khi TẤT CẢ các bài test đều Pass (Đặc biệt là tính năng Reconnect WebSocket và AI RAG), bạn mới tạo một môi trường **Production**, sao chép các biến môi trường sang và deploy bản chính thức.

---

## 7. Quy Trình Cứu Hộ / Rollback (Phase 13)

Nếu bản cập nhật gây lỗi hệ thống:
1. **Code Frontend/Backend**: Trong giao diện Railway, vào tab **Deployments** của Service bị lỗi. Tìm bản deploy cũ đang chạy ổn định, nhấn vào dấu 3 chấm (...), và chọn **Redeploy**.
2. **Cấu Hình**: Nếu lỗi do biến môi trường, hãy sửa lại trong tab **Variables** (Railway có lưu lịch sử thay đổi biến).
3. **Database**: KHÔNG được tự động rollback database migrations. Luôn ưu tiên viết code mới để sửa (forward-fix). Nếu đặc biệt nghiêm trọng, vào Terminal của Railway gõ `alembic downgrade -1` *TRƯỚC KHI* rollback code Backend.

---

## 8. Giám Sát và Tối Ưu Chi Phí (Phases 14 & 15)

- **Giám Sát (Metrics)**: Sử dụng tab **Metrics** có sẵn của Railway để theo dõi CPU, RAM, và Network.
- **Cảnh báo RAM**: AI ChromaDB ngốn khá nhiều RAM khi xử lý vector dữ liệu. Nếu Backend Service hay bị sập ngẫu nhiên với lỗi `OOMKilled` (Out of Memory), bạn cần nới lỏng giới hạn RAM cho Backend trong Railway (chọn gói tài nguyên cao hơn).
- **Chi phí**: Railway tính tiền theo mức sử dụng (pay-as-you-go). Để tiết kiệm nhất, đừng bật tính năng Scale (Replicas) nếu chưa thực sự có nhiều người dùng. Mặc định 1 Replica cho mỗi service là đủ.
