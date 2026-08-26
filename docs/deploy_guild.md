# MemoryChat — Hướng dẫn deploy lên Railway (từng bước)

Tài liệu này hướng dẫn **bấm từng nút** để đưa MemoryChat lên Railway: Staging trước, Production sau.

Nguồn kiến trúc: [`plan/MEMORYCHAT_RAILWAY_DEPLOYMENT_PLAN.md`](./plan/MEMORYCHAT_RAILWAY_DEPLOYMENT_PLAN.md).  
Cẩm nang vận hành ngắn: [`MEMORYCHAT_RAILWAY_DEPLOYMENT.md`](./MEMORYCHAT_RAILWAY_DEPLOYMENT.md).  
Checklist test: [`SMOKE_TESTING.md`](./SMOKE_TESTING.md).

**Không** lặp lại 20 pha pre-deployment. Hệ thống hiện tại đã sẵn sàng deploy.

---

## Mục lục

1. [Bạn sẽ có gì khi xong](#1-bạn-sẽ-có-gì-khi-xong)
2. [Nguyên tắc bắt buộc](#2-nguyên-tắc-bắt-buộc)
3. [Kiến trúc trên Railway](#3-kiến-trúc-trên-railway)
4. [Chuẩn bị trước khi mở Railway](#4-chuẩn-bị-trước-khi-mở-railway)
5. [Bảng biến môi trường (copy đúng)](#5-bảng-biến-môi-trường-copy-đúng)
6. [Thứ tự triển khai — đừng đảo](#6-thứ-tự-triển-khai--đừng-đảo)
7. [Bước 1 — Tài khoản Railway + GitHub](#bước-1--tài-khoản-railway--github)
8. [Bước 2 — Tạo Project và môi trường Staging](#bước-2--tạo-project-và-môi-trường-staging)
9. [Bước 3 — Thêm PostgreSQL](#bước-3--thêm-postgresql)
10. [Bước 4 — Deploy Backend (FastAPI)](#bước-4--deploy-backend-fastapi)
11. [Bước 5 — Volume ChromaDB](#bước-5--volume-chromadb)
12. [Bước 6 — Domain Backend + Healthcheck](#bước-6--domain-backend--healthcheck)
13. [Bước 7 — Chạy Alembic migration](#bước-7--chạy-alembic-migration)
14. [Bước 8 — Deploy Frontend (Next.js)](#bước-8--deploy-frontend-nextjs)
15. [Bước 9 — Nối CORS và rebuild Frontend](#bước-9--nối-cors-và-rebuild-frontend)
16. [Bước 10 — Kiểm tra HTTPS / WSS](#bước-10--kiểm-tra-https--wss)
17. [Bước 11 — Smoke test Staging](#bước-11--smoke-test-staging)
18. [Bước 12 — Deploy Production](#bước-12--deploy-production)
19. [Giám sát sau khi lên](#19-giám-sát-sau-khi-lên)
20. [Rollback khi hỏng](#20-rollback-khi-hỏng)
21. [Chi phí](#21-chi-phí)
22. [Troubleshooting](#22-troubleshooting)
23. [Checklist thành công](#23-checklist-thành-công)

---

## 1. Bạn sẽ có gì khi xong

```text
Internet
   │
   ├── HTTPS  →  Frontend  (Next.js)     https://xxxxx.up.railway.app
   └── WSS    →  Backend   (FastAPI)     wss://yyyyy.up.railway.app/ws/chat
                    │
                    ├── PostgreSQL  (managed, private)
                    └── Volume /app/data  (ChromaDB)
```

Ba service trên cùng một Railway Project:

| Service | Vai trò | Nguồn build |
|---|---|---|
| `Postgres` | Database quan hệ (user, chat, connections…) | Railway plugin |
| `backend` | FastAPI + WebSocket + AI workers + ChromaDB nhúng | `Dockerfile` ở **root repo** |
| `frontend` | Next.js UI + BFF proxy + cookie session | `frontend/Dockerfile` |

ChromaDB **không** tách service riêng. Nó chạy trong process backend, ghi file vào `./data/chroma` → bắt buộc gắn Volume.

---

## 2. Nguyên tắc bắt buộc

1. Deploy **Staging trước**. Chỉ lên Production khi smoke test Staging pass.
2. PostgreSQL là service riêng. Không chạy Postgres trong container backend.
3. **Không commit** file `.env` hay secret thật.
4. **Không** đưa `JWT_SECRET`, `OPENAI_API_KEY`, `DATABASE_URL` vào biến `NEXT_PUBLIC_*`.
5. Backend **chỉ 1 replica** và **`--workers 1`**. Event bus + WebSocket manager nằm in-memory; nhiều process sẽ mất realtime.
6. **Không bật Serverless** cho backend (WebSocket bị cắt khi sleep).
7. Mỗi bước bên dưới có mục **Cách kiểm tra**. Đừng bỏ qua.
8. Không sửa code ứng dụng chỉ vì deploy, trừ khi gặp blocker thật.

---

## 3. Kiến trúc trên Railway

```text
Railway Project: MemoryChat
│
├── Environment: staging          ← làm cái này trước
│     ├── Postgres
│     ├── backend  + Volume /app/data
│     └── frontend
│
└── Environment: production       ← clone từ staging khi đã ổn
      ├── Postgres  (DB riêng, không dùng chung staging)
      ├── backend  + Volume riêng
      └── frontend
```

Frontend **không** gọi API backend trực tiếp từ browser cho REST. Browser gọi Next.js (`/api/auth/*`, `/api/proxy/*`), Next.js server mới gọi backend. Cookie login nằm trên domain frontend.

WebSocket thì khác: browser kết nối **thẳng** tới backend:

```text
Browser  →  POST /api/auth/ws-ticket  (Next.js)
         →  wss://<backend-host>/ws/chat?ticket=...
```

Vì vậy `NEXT_PUBLIC_API_URL` phải là origin backend **không** có đuôi `/api/v1`. Code frontend ghép path `/api/v1/...` và lấy `host` từ URL này để mở WSS.

---

## 4. Chuẩn bị trước khi mở Railway

Làm hết checklist này trên máy bạn (Windows cũng được).

### 4.1. Tài khoản và repo

- [ ] Tài khoản [Railway](https://railway.com) — gói **Hobby** trở lên (trial/free có hạn mức build + volume).
- [ ] Thẻ thanh toán đã gắn trên Railway (Hobby yêu cầu).
- [ ] Repo GitHub đã push code hiện tại. Origin hiện tại của project này:

  `https://github.com/Soetiee2207/P214-clone.git`

  Railway đọc GitHub, **không** đọc ổ `E:\` của bạn. Mọi thay đổi phải `git push` trước khi Railway build được bản mới.

- [ ] Railway được phép đọc GitHub repo đó:
  1. Vào [GitHub → Settings → Applications → Authorized OAuth Apps / GitHub Apps](https://github.com/settings/installations) sau khi login Railway lần đầu.
  2. Grant quyền repo (private cũng được).

### 4.2. API key LLM

Cần **một** trong hai:

| Cách | Biến | Ghi chú |
|---|---|---|
| OpenAI (mặc định) | `OPENAI_API_KEY` | Dùng `gpt-4o-mini` + `text-embedding-3-small` |
| OpenRouter | `USE_OPENROUTER=true` + `OPENROUTER_API_KEY` | Rẻ hơn; embeddings vẫn cần key OpenAI-compatible |

Không có key thì chat REST/WS vẫn chạy, nhưng Search/Copilot/Memory AI sẽ lỗi khi được gọi.

### 4.3. Sinh JWT_SECRET

**Không** dùng giá trị mặc định `local-dev-secret-change-in-production`. Backend **từ chối start** nếu `APP_ENV=production` hoặc `staging` mà secret chưa đổi.

PowerShell:

```powershell
[Convert]::ToHexString([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32)).ToLower()
```

Git Bash / macOS / Linux:

```bash
openssl rand -hex 32
```

Copy chuỗi ra notepad tạm. **Không** commit vào git.

### 4.4. Hiểu PORT của Railway

Railway gán `$PORT` lúc runtime. Dockerfile backend đang hardcode port `8000`:

```dockerfile
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

Trên Railway bạn **phải** ghi đè Start Command (Bước 4.6). Nếu quên, healthcheck fail vì Railway ping nhầm cổng.

### 4.5. (Tuỳ chọn) Railway CLI

Không bắt buộc. Dashboard đủ để deploy. Nếu muốn shell/logs từ máy:

```powershell
npm i -g @railway/cli
railway login
```

---

## 5. Bảng biến môi trường (copy đúng)

Đặt trên tab **Variables** của từng service. **Không** tạo file `.env` trên Railway. **Không** dán secret vào tài liệu này / PR / chat công khai.

### 5.1. Backend (`backend` service)

| Variable | Bắt buộc | Secret | Giá trị | Mục đích |
|---|---|---|---|---|
| `APP_ENV` | Có | Không | `staging` rồi `production` | Bật kiểm tra bảo mật lúc start |
| `DEBUG` | Có | Không | `false` | Production cấm `true` |
| `LOG_LEVEL` | Có | Không | `INFO` | Cấm `DEBUG` khi `APP_ENV` là staging/production |
| `DATABASE_URL` | Có | Có | `${{Postgres.DATABASE_URL}}` | Kết nối Postgres nội bộ. Tên service phải khớp (mặc định `Postgres`) |
| `JWT_SECRET` | Có | Có | chuỗi 64 hex bạn vừa sinh | Ký JWT. Đổi = user phải login lại |
| `JWT_EXPIRE_MINUTES` | Không | Không | `60` | TTL access token |
| `CORS_ORIGINS` | Có | Không | `https://<frontend>.up.railway.app` | **Không** dấu `/` cuối. **Không** dùng `*` |
| `OPENAI_API_KEY` | Có* | Có | `sk-...` | *Bắt buộc nếu không dùng OpenRouter |
| `MODEL_NAME` | Không | Không | `gpt-4o-mini` | Chat/copilot |
| `EMBEDDING_MODEL` | Không | Không | `text-embedding-3-small` | RAG |
| `LLM_TIMEOUT` | Không | Không | `30` | Timeout gọi LLM (giây) |
| `CHROMA_PERSIST_DIR` | Có | Không | `/app/data/chroma` | Đúng path Volume |
| `AI_LOG_DIR` | Không | Không | `/app/data/ai-log` | Log prompt; nằm trong Volume thì không mất khi redeploy |
| `RAILWAY_RUN_UID` | Có | Không | `0` | Volume mount quyền root; image chạy `appuser` — không set thì ChromaDB không ghi được file |
| `USE_OPENROUTER` | Không | Không | `true` / `false` | Đổi provider |
| `OPENROUTER_API_KEY` | Không | Có | `sk-or-...` | Chỉ khi `USE_OPENROUTER=true` |
| `OPENROUTER_MODEL` | Không | Không | `openai/gpt-4o-mini` | Model trên OpenRouter |

Cách thêm `DATABASE_URL` dạng **Variable Reference** (đừng paste connection string public):

1. Tab **Variables** của `backend`.
2. **Add Variable** → **Add a Variable Reference** (hoặc gõ `${{`).
3. Chọn service Postgres → `DATABASE_URL`.
4. Kết quả phải giống: `${{Postgres.DATABASE_URL}}`.

Nếu tên service Postgres của bạn là `PostgreSQL` thì dùng `${{PostgreSQL.DATABASE_URL}}`. Click vào service Postgres trên canvas để xem tên.

### 5.2. Frontend (`frontend` service)

| Variable | Bắt buộc | Secret | Giá trị | Mục đích |
|---|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | Có | Không | `https://<backend>.up.railway.app` | Origin backend. **Không** thêm `/api/v1`. **Không** dấu `/` cuối |
| `NODE_ENV` | Không | Không | `production` | Dockerfile đã set |

Bật **Available at Build Time** cho `NEXT_PUBLIC_API_URL`. Next.js nhúng `NEXT_PUBLIC_*` lúc `npm run build`. Đổi giá trị mà không **Rebuild** thì browser vẫn trỏ URL cũ.

`NEXT_PUBLIC_WS_URL` **không được code frontend hiện tại đọc**. Đừng đặt với kỳ vọng nó đổi WebSocket. WS lấy host từ `NEXT_PUBLIC_API_URL`.

### 5.3. Những biến tuyệt đối không đặt trên frontend

`JWT_SECRET`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `DATABASE_URL`, `PGPASSWORD`.

---

## 6. Thứ tự triển khai — đừng đảo

```text
1. GitHub connected
2. Project + environment staging
3. PostgreSQL
4. Backend service + biến + Volume + Start Command
5. Generate domain backend
6. Migration Alembic
7. Healthcheck backend thật (HTTP 200)
8. Frontend service + biến (build-time)
9. Generate domain frontend
10. Cập nhật CORS_ORIGINS = domain frontend
11. Rebuild frontend (vì NEXT_PUBLIC_API_URL)
12. Smoke test
13. (Sau khi pass) nhân bản sang production
```

---

## Bước 1 — Tài khoản Railway + GitHub

1. Mở [https://railway.com](https://railway.com) → **Login** bằng GitHub (khuyến nghị, ít bước hơn).
2. Nếu login bằng email: vào dashboard → avatar → **Configure GitHub App** → Install vào account chứa repo `P214-clone` (hoặc repo bạn dùng).
3. Chọn **All repositories** hoặc chỉ repo MemoryChat.
4. Confirm.

**Cách kiểm tra:** Dashboard hiện nút **New Project**. Khi tạo service từ GitHub, repo của bạn nằm trong danh sách.

---

## Bước 2 — Tạo Project và môi trường Staging

1. Dashboard → **New Project**.
2. Chọn **Empty Project** (không chọn template Next.js/FastAPI sẵn — ta dùng Dockerfile của repo).
3. Đặt tên project: `MemoryChat`.
4. Góc trên canvas, môi trường mặc định thường là `production`. Đổi / tạo **staging**:
   - Click tên environment (thường góc trên-trái).
   - **Create Environment** → tên `staging`.
   - Làm **toàn bộ bước 3–11 trên `staging`**.

Nếu UI không cho tạo environment (gói hạn chế): đặt `APP_ENV=staging` trên service và coi project này là staging. Tạo project thứ hai tên `MemoryChat-prod` khi lên production.

**Cách kiểm tra:** Canvas trống, badge environment = `staging`.

---

## Bước 3 — Thêm PostgreSQL

1. Trên canvas, bấm **+ New** (hoặc `Ctrl+K` / `Cmd+K`).
2. **Database** → **PostgreSQL**.
3. Đợi status **Online** (vài chục giây).
4. Click service Postgres → tab **Variables**. Bạn sẽ thấy `DATABASE_URL`, `PGHOST`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`, `PGPORT`.
5. **Settings → Networking**: **đừng** bật Public / TCP Proxy trừ khi bạn cần DBeaver từ máy local. App backend kết nối qua mạng nội bộ Railway (`*.railway.internal`), không cần public.

Bật backup nếu gói cho phép: click volume/database → **Backups** → daily.

**Cách kiểm tra:**

- Service Postgres **Online**.
- Có biến `DATABASE_URL` dạng `postgresql://...@....railway.internal:5432/...`.
- Không có public domain trên Postgres.

---

## Bước 4 — Deploy Backend (FastAPI)

### 4.1. Tạo service từ GitHub

1. Canvas → **+ New** → **GitHub Repo**.
2. Chọn repo MemoryChat (`P214-clone` hoặc repo bạn push).
3. Railway tạo service và **tự build ngay**. Build đầu thường fail vì chưa có biến — bình thường.
4. Click service vừa tạo → **Settings → General**:
   - **Name:** `backend`
   - **Root Directory:** để trống / `/` (Dockerfile nằm ở root).
   - **Watch Paths** (tiết kiệm build):

     ```text
     src/**
     alembic/**
     alembic.ini
     requirements.txt
     Dockerfile
     .dockerignore
     ```

### 4.2. Xác nhận Railway dùng Dockerfile

**Settings → Build**:

- Builder = **Dockerfile**.
- Dockerfile path = `Dockerfile` (mặc định).

Nếu hiện Railpack/Nixpacks: chọn **Dockerfile** thủ công.

### 4.3. Tắt Serverless, 1 replica

**Settings → Deploy** (hoặc Scaling):

- Replicas = **1**.
- Serverless / App Sleeping = **Off**.

### 4.4. Biến môi trường backend

Tab **Variables** → thêm đúng bảng [§5.1](#51-backend-backend-service).

Tạm thời `CORS_ORIGINS` có thể để:

```text
http://localhost:3000
```

Bạn sẽ sửa thành domain frontend ở Bước 9. `APP_ENV=staging` **không** cấm localhost, chỉ cấm `*`.

`DATABASE_URL` phải là reference, ví dụ:

```text
${{Postgres.DATABASE_URL}}
```

Nếu SQLAlchemy báo `Can't load plugin: sqlalchemy.dialects:postgres` (URL bắt đầu `postgres://` thay vì `postgresql://`), xoá reference và tạo tay:

```text
postgresql://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/${{Postgres.PGDATABASE}}
```

### 4.5. Start Command — bắt buộc có `/bin/sh -c`

Dockerfile deploy trên Railway ghi đè `CMD` theo **exec form**, **không** expand `$PORT` trừ khi bọc shell.

**Settings → Deploy → Custom Start Command:**

```bash
/bin/sh -c "exec uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1"
```

Đúng từng ký tự. `--workers 1` là bắt buộc.

### 4.6. Pre-Deploy Command (migration tự chạy mỗi deploy)

**Settings → Deploy → Pre-Deploy Command:**

```bash
alembic upgrade head
```

Pre-deploy **không** mount Volume (Chroma không liên quan). Nó chạy trong image đã build, có `DATABASE_URL`, phù hợp Alembic.

Nếu pre-deploy fail, Railway **không** đẩy bản mới ra internet — đúng ý muốn.

### 4.7. Healthcheck

**Settings → Deploy → Healthcheck Path:**

```text
/health/readiness
```

Timeout: `300` giây (backend lần đầu import LangChain/Chroma hơi chậm).

Endpoint này `SELECT 1` lên Postgres. HTTP 200 = DB sống. Đừng dùng `/health` (không tồn tại). Có `/health/liveness` nếu chỉ cần process sống, không đủ cho production.

**Cách kiểm tra bước 4 (chưa cần domain public):**

- Tab **Deployments**: build **Success**.
- Logs có `app_starting`, `outbox_worker_started`, `memory_worker_started`.
- Không có `FATAL: JWT Secret must be changed`.
- Không crash loop.

Nếu fail, đọc [§22](#22-troubleshooting) trước khi sang bước 5.

---

## Bước 5 — Volume ChromaDB

ChromaDB dùng `chromadb.PersistentClient(path=...)`. Không gắn volume thì mỗi lần redeploy **mất toàn bộ embedding**. RAG/search AI phải index lại từ đầu.

1. Canvas → click service `backend`.
2. **Settings → Volumes** → **Add Volume**  
   (hoặc canvas: chuột phải → **Volume**, attach vào `backend`).
3. **Mount Path:**

   ```text
   /app/data
   ```

   Đúng path này. Code mặc định `./data/chroma` với `WORKDIR /app` → `/app/data/chroma`. Biến `CHROMA_PERSIST_DIR=/app/data/chroma` khớp mount.

4. Size ban đầu: **1 GB** đủ MVP. Resize sau trên gói trả phí, không downtime.
5. Confirm biến `RAILWAY_RUN_UID=0` đã có (Bước 4.4). Image `USER appuser`; volume mount là root → không set UID thì permission denied khi ghi chroma.
6. Redeploy backend (**Deployments → ⋮ → Redeploy**) để volume được mount. Volume **không** có lúc build, chỉ lúc start.

**Lưu ý:** Service có volume **không** zero-downtime. Mỗi redeploy có vài giây downtime. Chấp nhận được với MVP.

**Cách kiểm tra:**

- Trên canvas, `backend` có icon volume.
- Logs không còn `Permission denied: /app/data`.
- Sau khi dùng AI search một lần, vào Railway CLI (tuỳ chọn):

  ```bash
  railway volume browse /app/data
  ```

  Thấy thư mục `chroma/`.

---

## Bước 6 — Domain Backend + Healthcheck

1. Click `backend` → **Settings → Networking**.
2. **Generate Domain**. Nhận hostname dạng:

   ```text
   backend-production-xxxx.up.railway.app
   ```

   Ghi lại. Đây là **Backend Origin**. Gọi nó `BACKEND_HOST` trong các bước sau.

3. Target port: để Railway dùng `$PORT` (đừng hardcode 8000).
4. Đợi deployment **Active**.

**Cách kiểm tra — phải có HTTP 200 thật, không chỉ “container started”:**

Trình duyệt hoặc PowerShell:

```powershell
curl https://BACKEND_HOST/health/liveness
curl https://BACKEND_HOST/health/readiness
```

Kỳ vọng:

```json
{"status":"ok","version":"1.0.0-mvp"}
```

```json
{"status":"ok","version":"1.0.0-mvp","db":"ok"}
```

Nếu readiness = 503: Postgres chưa reference đúng, hoặc SQLAlchemy URL sai scheme.

Mở thêm:

```text
https://BACKEND_HOST/docs
```

Swagger FastAPI hiện = routing OK. (Có thể để public lúc staging; production cân nhắc tắt docs nếu muốn.)

---

## Bước 7 — Chạy Alembic migration

Nếu Pre-Deploy Command (Bước 4.6) đã thành công, bảng đã có. Vẫn **xác minh**.

### Cách A — Pre-deploy logs (ưu tiên)

Deployments → bản mới nhất → log pre-deploy. Thấy Alembic `Running upgrade ... -> ...` và exit 0.

### Cách B — Railway terminal / one-off

1. Service `backend` → tab **Terminal** (hoặc **+ New** → one-off command, tuỳ UI).
2. Chạy:

   ```bash
   alembic current
   alembic upgrade head
   alembic current
   ```

Head hiện tại của repo gồm các revision trong `alembic/versions/`, trong đó có:

- `8f671eb1297d` — p2p init
- `00b16a0c0c78` — connection requests
- `4e043bb0add2` — indexes + constraints
- `4e9a18f8ea91` — last_message_content
- `5c3d2a1b8e4f` — contacts / recommendations
- `6d4e3f2a1b0c` — user profiles

### Cách C — Data tab Postgres

Click Postgres → **Data** (Query). Chạy:

```sql
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY 1;
```

Phải thấy các bảng user, conversation, message, connection, v.v. — không phải database trống.

**Không** dùng `Base.metadata.create_all()` thay Alembic.

**Cách kiểm tra:** `alembic current` trùng revision mới nhất; readiness vẫn 200.

---

## Bước 8 — Deploy Frontend (Next.js)

Cùng **một** GitHub repo, service thứ hai, root directory khác.

### 8.1. Tạo service

1. Canvas → **+ New** → **GitHub Repo** → chọn **đúng repo** lần nữa.
2. **Settings → General:**
   - **Name:** `frontend`
   - **Root Directory:** `frontend`
   - **Watch Paths:**

     ```text
     frontend/**
     ```

3. **Settings → Build:** Dockerfile path để mặc định (`Dockerfile` trong thư mục `frontend`).

Railway sẽ nhận `frontend/Dockerfile` (multi-stage, `output: standalone`).

### 8.2. Domain frontend trước khi build (tránh bake URL sai)

1. `frontend` → **Settings → Networking → Generate Domain**.
2. Ghi lại `FRONTEND_HOST`, ví dụ `frontend-xxxx.up.railway.app`.
3. URL đầy đủ: `https://FRONTEND_HOST` — **không** dấu `/` cuối.

### 8.3. Biến frontend

Tab **Variables**:

```text
NEXT_PUBLIC_API_URL=https://BACKEND_HOST
```

Thay `BACKEND_HOST` bằng hostname Bước 6, **không** `https://BACKEND_HOST/api/v1`.

Bật **Available at Build Time** cho biến này.

Dockerfile đã có:

```dockerfile
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
RUN npm run build
```

Không bật build-time → `npm run build` nhận chuỗi rỗng → browser fallback `http://127.0.0.1:8000`.

### 8.4. Start Command frontend

**Không** set Custom Start Command. Image đã:

```dockerfile
CMD ["node", "server.js"]
```

Next standalone đọc `$PORT` Railway lúc runtime. `ENV PORT=3000` trong Dockerfile bị runtime ghi đè.

### 8.5. Healthcheck frontend

**Settings → Deploy → Healthcheck Path:** `/`

Timeout `120`.

Replicas = 1. Serverless có thể bật cho frontend (không giữ WS), nhưng lần đầu hãy **tắt** cho dễ debug.

**Cách kiểm tra:**

- Deployment Success.
- Mở `https://FRONTEND_HOST` thấy trang login/register MemoryChat, không phải 502.
- DevTools → Network: **không** có request tới `localhost` / `127.0.0.1`.

---

## Bước 9 — Nối CORS và rebuild Frontend

Hai service phải trỏ vào nhau. Làm đúng thứ tự:

### 9.1. Backend CORS

`backend` → Variables → sửa:

```text
CORS_ORIGINS=https://FRONTEND_HOST
```

Nhiều origin (staging + custom domain) thì cách nhau bởi dấu phẩy, **không** khoảng trắng thừa nếu bạn không chắc code `split(",")` đã `strip` — hiện tại code **không strip**:

```python
allow_origins=settings.cors_origins.split(",")
```

Vì vậy **đừng** viết `https://a.com, https://b.com` (có space). Viết:

```text
https://a.com,https://b.com
```

Không trailing slash. `https://foo.up.railway.app/` ≠ `https://foo.up.railway.app`.

Redeploy **backend** sau khi đổi CORS.

### 9.2. Rebuild frontend

Nếu bạn generate domain backend **sau** lần build frontend đầu, bắt buộc:

`frontend` → Deployments → **⋮ → Redeploy**  
và chọn rebuild từ source (không dùng image cũ). Đổi `NEXT_PUBLIC_API_URL` mà chỉ Restart thì **không** đủ.

**Cách kiểm tra:**

1. `https://FRONTEND_HOST/register` tạo user.
2. Login thành công, vào được khu vực app (`/chats`).
3. DevTools → Application → Cookies: có `memorychat_session` (httpOnly, Secure).
4. Network: gọi `/api/auth/login`, `/api/proxy/api/v1/...` status 2xx, không 502 Proxy error.

---

## Bước 10 — Kiểm tra HTTPS / WSS

REST ổn **không** có nghĩa WebSocket ổn. Phải test riêng.

### 10.1. HTTPS

```text
https://FRONTEND_HOST
https://BACKEND_HOST/health/readiness
```

Ổ khoá trình duyệt, certificate Railway. Không mixed content.

### 10.2. WSS

1. Login trên staging.
2. F12 → tab **Network** → filter **WS**.
3. Mở trang chat.
4. Phải thấy connection tới:

   ```text
   wss://BACKEND_HOST/ws/chat?ticket=...
   ```

   Status **101 Switching Protocols**.
5. Messages tab: server gửi `{"type":"ping"}`, client trả `{"type":"pong"}` mỗi ~30s.

Nếu WS URL là `ws://localhost:8000` → `NEXT_PUBLIC_API_URL` không được bake lúc build. Quay lại Bước 8.3 + 9.2.

Nếu 1006/1008 ngay: ticket fail (cookie) hoặc CORS/origin. Xem §22.

### 10.3. Custom domain (tuỳ chọn, làm sau khi Staging ổn)

1. Service → Networking → **Custom Domain** → `chat.yourdomain.com` (frontend), `api.yourdomain.com` (backend).
2. DNS: CNAME theo hướng dẫn Railway.
3. Đợi TLS Ready.
4. Cập nhật:
   - Frontend `NEXT_PUBLIC_API_URL=https://api.yourdomain.com` + rebuild
   - Backend `CORS_ORIGINS=https://chat.yourdomain.com`
5. Cookie `secure` đã bật khi `NODE_ENV=production`. Giữ frontend/backend **cùng site** nếu sau này muốn cookie cross-subdomain; kiến trúc hiện tại cookie chỉ nằm trên frontend nên khác subdomain vẫn được.

**Không** public Postgres.

---

## Bước 11 — Smoke test Staging

Chạy checklist [`SMOKE_TESTING.md`](./SMOKE_TESTING.md). Tóm tắt thao tác tay với **hai browser** (Chrome + ẩn danh) / hai user.

### Auth

- [ ] Register user A, user B
- [ ] Login / Logout
- [ ] Sai mật khẩu bị từ chối
- [ ] Refresh trang vẫn đăng nhập (cookie)

### Connection requests

- [ ] A gửi request cho B — B nhận realtime
- [ ] B reject — A thấy
- [ ] A gửi lại, B accept — hai bên có trong danh sách
- [ ] Remove/cancel — không chat được nữa

### Chat

- [ ] Mở conversation, A gửi, B nhận **ngay** (không cần reload)
- [ ] Refresh: tin nhắn còn
- [ ] Scroll lên: cursor pagination, không duplicate
- [ ] A recall: B thấy recalled realtime; refresh vẫn recalled

### WebSocket reconnect

- [ ] DevTools Offline vài giây rồi Online
- [ ] WS tự connect lại, không nhân đôi tin
- [ ] Gửi tin sau reconnect OK

### AI (nếu có key)

- [ ] Copilot / AI Hub không 500
- [ ] Search RAG trả context đúng conversation của user đó
- [ ] User A **không** search được nội dung chat của B–C

### Reliability

- [ ] Redeploy backend: frontend báo reconnect, rồi chat lại được
- [ ] Volume còn: search AI không “quên” hết sau redeploy (cần đã index trước đó)

**Fail bất kỳ mục nào trên Staging → không làm Bước 12.**

---

## Bước 12 — Deploy Production

Chỉ khi Bước 11 pass.

### 12.1. Tạo environment production

1. Project → **Create Environment** → `production` → duplicate từ `staging` **nếu UI cho clone variables**.
2. **Không** share Postgres với staging. Add **Postgres mới** trên production.
3. Volume **mới** cho backend production (không mount volume staging).
4. Generate domain production riêng (hoặc custom domain thật).

Hoặc: Project Railway thứ hai `MemoryChat-prod`, lặp Bước 3–10 với `APP_ENV=production`.

### 12.2. Biến production — khác staging

| Variable | Production |
|---|---|
| `APP_ENV` | `production` |
| `DEBUG` | `false` |
| `LOG_LEVEL` | `INFO` |
| `JWT_SECRET` | **Secret mới**, đừng copy staging nếu staging đã lộ |
| `CORS_ORIGINS` | Đúng domain production, không localhost |
| `DATABASE_URL` | Reference Postgres **production** |
| `NEXT_PUBLIC_API_URL` | Origin backend **production** + Available at Build Time |

### 12.3. Thứ tự release

```text
1. Tag git (ví dụ v1.0.0) và ghi commit SHA
2. Đối chiếu Variables production
3. Backup Postgres (Railway Backups / dump)
4. Deploy backend (pre-deploy chạy alembic upgrade head)
5. curl /health/readiness → 200
6. Kiểm tra WSS 101
7. Deploy / rebuild frontend
8. Smoke test production (rút gọn: register, chat 2 user, recall, 1 câu AI)
9. Xem logs 15–30 phút
10. Mới tuyên bố thành công
```

Không merge/deploy code không liên quan trong cửa sổ release.

---

## 19. Giám sát sau khi lên

### Logs

Service → tab **Logs**. Filter:

- `health_check_db_failed`
- `Proxy error`
- `OOM`
- `FATAL`
- `Rate Limit Exceeded`

### Metrics

Tab **Metrics**: CPU, RAM, Network.

Backend dễ **OOMKilled** vì Chroma + LangChain. Nếu RAM sát trần:

- Nâng memory limit backend (Hobby có trần; Pro cao hơn).
- Không tăng replica (sẽ gãy WS).
- Chỉ scale dọc (thêm RAM), không scale ngang.

### Health

Railway healthcheck **chỉ lúc deploy**, không monitor liên tục. Có thể ping ngoài:

```text
https://BACKEND_HOST/health/readiness
```

bằng UptimeRobot / cron.

### Metrics app

Backend expose Prometheus tại `/metrics` (instrumentator). Không bắt buộc gắn Grafana lúc MVP.

### Backup

- Postgres: bật Railway automatic backups.
- Chroma volume: Settings volume → Backups (nếu có). Embedding mất thì rebuild được từ Postgres/memory records, nhưng search AI tạm trống.
- **Không** rollback migration tự động — xem §20.

### Cảnh báo thực tế nên để mắt

| Hiện tượng | Ý nghĩa |
|---|---|
| Readiness 503 | Mất Postgres |
| 5xx tăng sau deploy | Release hỏng → rollback image |
| WS disconnect hàng loạt | Redeploy volume / OOM / serverless sleep |
| Latency AI > 30s | LLM timeout, check `LLM_TIMEOUT` / provider |
| Disk volume 90%+ | Resize volume |

---

## 20. Rollback khi hỏng

Chi tiết: [`ROLLBACK_PLAN.md`](./ROLLBACK_PLAN.md). Trên Railway làm như sau.

### Backend / Frontend code

1. Service lỗi → **Deployments**.
2. Tìm bản **Active** trước đó (SHA biết là tốt).
3. **⋮ → Redeploy**.

Không `git revert` lung tung trên `main` trong lúc cháy.

### Variables

Tab Variables có lịch sử. Restore giá trị cũ, redeploy. Frontend đổi `NEXT_PUBLIC_*` phải **rebuild**.

### Database

**Không** `alembic downgrade` mặc định.

- Migration chỉ **thêm cột nullable / bảng mới** → để nguyên, rollback code được.
- Migration **xoá cột / đổi kiểu** → không rollback DB; forward-fix bằng migration mới.

Nếu bắt buộc downgrade (hiếm):

```bash
alembic downgrade -1
```

chạy **trước** khi redeploy code cũ, trên terminal backend, và chỉ khi bạn đã đọc file revision.

### Volume / Chroma

Rollback code không xoá volume. Nếu volume corrupt: restore backup volume, hoặc xoá collection để worker index lại.

---

## 21. Chi phí

Ước lượng MVP ít user, region Singapore/US, **không** phải báo giá chính thức.

| Hạng mục | Gợi ý ban đầu | Ghi chú |
|---|---|---|
| Railway Hobby | ~$5/tháng | Trần usage; vượt thì tính thêm |
| Frontend | 0.5–1 vCPU, 512 MB | Rẻ |
| Backend | 1 vCPU, 1–2 GB RAM | Đừng để 512 MB |
| PostgreSQL | instance nhỏ + volume | Backup tính thêm |
| Volume Chroma 1 GB | rất nhỏ | Tăng khi RAG lớn |
| OpenAI `gpt-4o-mini` | vài USD lúc ít user | Xem [`guide/cost-management.md`](./guide/cost-management.md) |
| Embeddings | theo số memory được index | Đừng re-embed toàn bộ mỗi deploy |
| Egress | tăng nếu public Postgres / media | Giữ DB private |

Chưa scale replica. Chưa thêm Redis/Chroma service riêng. Chưa HA Postgres.

---

## 22. Troubleshooting

### Build backend fail — `COPY` / Docker

- Root Directory phải là `/`, không phải `frontend`.
- `requirements.txt` phải ở root (`.dockerignore` không ignore file này).

### Build frontend fail — `npm ci` / standalone

- Root Directory = `frontend`.
- Có `package-lock.json`.
- RAM build Next.js: nếu OOM lúc build, tăng builder resources.

### Backend crash: `FATAL: JWT Secret must be changed`

`APP_ENV` là `staging`/`production` mà `JWT_SECRET` còn default. Đổi secret, redeploy.

### Backend crash: `LOG_LEVEL cannot be DEBUG` / `Debug mode must be disabled`

Set `LOG_LEVEL=INFO`, `DEBUG=false`.

### Backend crash: `CORS origins cannot contain wildcard '*'`

Xoá `*` trong `CORS_ORIGINS`.

### Healthcheck timeout / 502

- Start Command thiếu `/bin/sh -c` → app listen 8000, Railway ping `$PORT`.
- Healthcheck path sai (`/health` không tồn tại).
- Postgres chưa ready / `DATABASE_URL` sai.
- Tăng timeout 300s.

### `Service Unavailable: DB connection failed`

- Reference sai tên service (`Postgres` vs `PostgreSQL`).
- URL `postgres://` → đổi `postgresql://`.
- Postgres không cùng environment.
- Dùng `DATABASE_PUBLIC_URL` (TCP proxy) thay vì internal — chậm/lỗi SSL. Dùng internal.

### `Permission denied` `/app/data`

Thiếu `RAILWAY_RUN_UID=0` hoặc mount path không phải `/app/data`.

### Frontend mở được nhưng login 502 Proxy error

`NEXT_PUBLIC_API_URL` sai hoặc backend down. Log frontend sẽ có `Proxy error`. Test:

```powershell
curl https://BACKEND_HOST/api/v1/auth/login
```

(sẽ 422 vì thiếu body — chứng tỏ routing sống).

### Login OK nhưng chat không realtime

- WS không 101: xem Network/WS.
- URL `localhost`: quên Available at Build Time / chưa rebuild.
- Path phải là `/ws/chat`, không phải `/ws`.
- Backend 2 workers/2 replicas: event không tới user kia. Về 1 worker, 1 replica.
- Serverless sleep cắt WS.

### CORS error trên browser

REST đi qua Next proxy thì ít gặp CORS. Nếu thấy CORS: `CORS_ORIGINS` không khớp origin frontend (scheme/host/port/slash).

### AI 500 / empty search

- Thiếu `OPENAI_API_KEY`.
- Volume mới trống — chưa có embedding; nhắn vài tin, đợi worker.
- OpenRouter bật nhưng embedding vẫn cần OpenAI-compatible embeddings.

### Deploy thành công trên GitHub nhưng Railway không build

Watch Paths quá hẹp, hoặc service gắn nhầm branch. Settings → **Source** → branch `main` (hoặc branch bạn muốn).

### Thay env frontend không có hiệu lực

`NEXT_PUBLIC_*` bake lúc build. Redeploy **with rebuild**.

---

## 23. Checklist thành công

Chỉ đánh dấu khi **đã tự tay verify**, không phải vì build màu xanh.

```text
Repo GitHub private/public đã connect     ☐
Railway build Dockerfile backend          ☐
Railway build Dockerfile frontend         ☐
PostgreSQL private, cùng project          ☐
DATABASE_URL reference nội bộ             ☐
alembic upgrade head                      ☐
GET /health/readiness = 200 + db=ok       ☐
HTTPS frontend                            ☐
HTTPS backend                             ☐
WSS /ws/chat = 101 + ping/pong            ☐
Register / Login / Logout                 ☐
Connection request realtime               ☐
Chat realtime 2 user                      ☐
Recall realtime + persist sau refresh     ☐
Cursor pagination                         ☐
AI/RAG (nếu bật key)                      ☐
Chroma còn sau redeploy backend           ☐
Smoke test Staging pass                   ☐
Rollback (redeploy bản cũ) đã biết chỗ bấm ☐
Không secret trong git                    ☐
```

Trạng thái đích:

```text
                    🌐 Internet
                         │
                    HTTPS / WSS
                         │
                         ▼
                  ┌──────────────┐
                  │   Railway    │
                  │  Next.js     │
                  │  FastAPI     │
                  │  PostgreSQL  │
                  │  Volume*     │
                  └──────────────┘
* /app/data cho ChromaDB nhúng trong backend
```

---

## Phụ lục A — Lệnh xác minh nhanh (PowerShell)

Thay hai host sau khi Generate Domain:

```powershell
$backend  = "https://BACKEND_HOST"
$frontend = "https://FRONTEND_HOST"

curl "$backend/health/liveness"
curl "$backend/health/readiness"

# Expect 405 or 422, not 502/404:
curl -Method POST "$backend/api/v1/auth/login"

curl $frontend
```

Register + login (thay email):

```powershell
$reg = Invoke-RestMethod -Method POST "$backend/api/v1/auth/register" `
  -ContentType "application/json" `
  -Body '{"email":"a@example.com","password":"Passw0rd!","full_name":"Alice"}'

$login = Invoke-RestMethod -Method POST "$backend/api/v1/auth/login" `
  -ContentType "application/json" `
  -Body '{"email":"a@example.com","password":"Passw0rd!"}'

$login.access_token
```

Token trả về = auth backend OK. UI vẫn phải test cookie qua frontend.

---

## Phụ lục B — Mapping file trong repo

| Thành phần | File |
|---|---|
| Backend image | `/Dockerfile` |
| Frontend image | `/frontend/Dockerfile` |
| Compose local (không dùng trên Railway) | `/docker-compose.yml` |
| Settings / env names | `/src/config.py`, `/.env.example` |
| ASGI app | `/src/main.py` → `src.main:app` |
| Health | `GET /health/liveness`, `GET /health/readiness` |
| WS | `/src/api/ws.py` → `/ws/chat` |
| WS client | `/frontend/lib/ws/manager.ts` |
| BFF API URL | `/frontend/lib/api/client.ts` → `NEXT_PUBLIC_API_URL` |
| Alembic | `/alembic.ini`, `/alembic/env.py` |
| Chroma | `/src/services/vector_store.py` |

---

## Phụ lục C — Những điểm tài liệu cũ dễ làm sai

[`MEMORYCHAT_RAILWAY_DEPLOYMENT.md`](./MEMORYCHAT_RAILWAY_DEPLOYMENT.md) hữu ích nhưng một số chỗ **không khớp code hiện tại**. Guide này lấy code làm chuẩn:

| Chủ đề | Đúng với repo |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<backend>` — **không** `/api/v1` |
| `NEXT_PUBLIC_WS_URL` | Không dùng |
| WS path | `/ws/chat` |
| Start command Docker | Phải bọc `/bin/sh -c "... $PORT ..."` |
| User trong image | `appuser` → cần `RAILWAY_RUN_UID=0` khi gắn volume |

---

**Mục tiêu:** đưa đúng hệ thống MemoryChat đã ổn định lên Railway — không redesign.
```
