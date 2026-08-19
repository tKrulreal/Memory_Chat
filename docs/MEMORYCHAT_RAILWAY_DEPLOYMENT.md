# MemoryChat Railway Deployment Guide

This document is the official operational runbook for deploying the MemoryChat application to Railway. It conforms to the architecture and rules defined in `MEMORYCHAT_RAILWAY_DEPLOYMENT_PLAN.md`.

## 1. Railway Architecture Overview

MemoryChat requires a multi-service architecture on Railway:

1. **PostgreSQL Service**: Managed database for persistent relational data.
2. **Backend Service (FastAPI)**: Handles REST APIs, WebSockets, background AI workers, and ChromaDB.
3. **Frontend Service (Next.js)**: Handles the UI.

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

## 2. PostgreSQL Setup (Phase 5)

1. Create a **New Project** in Railway.
2. Click **Add a Plugin** -> **PostgreSQL**.
3. Railway will provision a Postgres database and automatically expose internal networking variables (e.g., `DATABASE_URL`).

---

## 3. Backend Deployment (Phases 2, 4, 6, 9)

### A. Create the Service
1. In your Railway Project, click **New** -> **GitHub Repo**.
2. Select your `MemoryChat` repository.
3. Under **Settings -> General**, set the **Root Directory** to `/` (default).

### B. Persistent Storage (ChromaDB)
Because ChromaDB stores vector embeddings locally, you MUST attach a volume so data survives redeploys.
1. Go to **Settings -> Volumes**.
2. Click **New Volume**.
3. Set the **Mount Path** to `/app/data`.

### C. Environment Variables (Secrets)
Go to the **Variables** tab of the Backend service and add:

| Variable | Secret | Value / Purpose |
|---|---|---|
| `DATABASE_URL` | Yes | *Use Reference: `${{Postgres.DATABASE_URL}}`* |
| `JWT_SECRET` | Yes | *Generate a strong secure random string* |
| `OPENAI_API_KEY` | Yes | *Your OpenAI key (or OpenRouter key)* |
| `APP_ENV` | No | `production` |
| `CORS_ORIGINS` | No | `https://your-frontend-domain.up.railway.app` |

*(Note: Never commit these to Git).*

### D. Start Command
Railway automatically injects a dynamic `$PORT`. You must override the default `uvicorn` command.
1. Go to **Settings -> Deploy**.
2. Set **Custom Start Command**:
   `uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1`

### E. Database Migration
Once the backend is deployed, you must run migrations to set up tables.
1. Go to **Deployments** -> **View Logs**.
2. Open the **Terminal** tab for the Backend service.
3. Run: `alembic upgrade head`
4. Verify the database tables exist in the PostgreSQL Data explorer.

---

## 4. Frontend Deployment (Phases 2, 4, 8)

### A. Create the Service
1. Click **New** -> **GitHub Repo**.
2. Select your `MemoryChat` repository again.
3. Under **Settings -> General**, set the **Root Directory** to `/frontend`.
*(Railway will automatically detect the Next.js `frontend/Dockerfile` and build it).*

### B. Environment Variables
Go to the **Variables** tab of the Frontend service and add:

| Variable | Secret | Value / Purpose |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | No | `https://<your-backend-railway-domain>/api/v1` |
| `NEXT_PUBLIC_WS_URL` | No | `wss://<your-backend-railway-domain>/ws` |

*Do NOT put JWT secrets or OpenAI keys here.*

### C. Start Command
The `frontend/Dockerfile` already exports `ENV PORT=3000` and uses `node server.js`. Railway will successfully override `$PORT` at runtime. No custom start command is necessary.

---

## 5. Domain Configuration (Phase 10)

1. For both Backend and Frontend, go to **Settings -> Networking**.
2. Click **Generate Domain** to get a free `.up.railway.app` domain, OR click **Custom Domain** to map your own domain.
3. Ensure the Frontend's `CORS_ORIGINS` matches the Frontend domain, and the Frontend's `NEXT_PUBLIC_*` URLs match the Backend domain.

---

## 6. Staging vs Production (Phases 11 & 12)

Do not deploy straight to Production. 
1. Create a Railway Environment named **Staging**.
2. Deploy the Frontend and Backend to Staging.
3. Run the [Smoke Test Checklist](./SMOKE_TESTING.md).
4. Only if all tests pass (including WebSocket reconnects and AI RAG queries), promote or replicate the environment variables to the **Production** environment.

---

## 7. Rollback Procedures (Phase 13)

If a deployment breaks:
1. **Frontend/Backend Code**: In Railway, go to the Service's **Deployments** tab. Find the previous stable deployment, click the three dots (...), and select **Redeploy**.
2. **Configuration**: If a bad environment variable caused the crash, revert it in the **Variables** tab (Railway tracks configuration history).
3. **Database**: Do NOT rollback migrations automatically. Always attempt a forward-fix. If critical, use `alembic downgrade -1` via the Railway Terminal *before* reverting the backend code.

---

## 8. Monitoring and Cost Control (Phases 14 & 15)

- **Metrics**: Use Railway's built-in **Metrics** tab to monitor CPU, RAM, and Network for both services.
- **RAM Warnings**: ChromaDB requires significant RAM during vector ingestion. If the Backend service restarts randomly with `OOMKilled` (Out of Memory), you must upgrade the Railway resource limits for the Backend.
- **Cost**: Railway charges based on usage. To minimize costs, ensure the Frontend and Backend do not have unnecessary horizontal scaling replicas enabled.
