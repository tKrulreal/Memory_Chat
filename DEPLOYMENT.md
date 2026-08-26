# MemoryChat - Deployment Guide

This document outlines the standard procedure for deploying MemoryChat to a production environment using Docker and Docker Compose. This ensures reproducibility across any host machine.

## Prerequisites

- **Docker** and **Docker Compose** installed on the host machine.
- **Git** (if pulling directly from the repository).
- At least 2GB of RAM (recommended).

## Step-by-Step Deployment

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/memorychat.git
cd memorychat
```

### 2. Configure the Environment
The application requires several environment variables (API keys, database URLs, secrets) to run.

```bash
cp .env.example .env
```

Edit the `.env` file using your preferred text editor (e.g., `nano .env` or `vim .env`). 

**Critical Variables for Production:**
- `APP_ENV=production` (Enforces strict security checks on startup).
- `DEBUG=false` (Must be false in production).
- `LOG_LEVEL=INFO` (Do not use DEBUG in production).
- `JWT_SECRET`: Must be changed to a secure, random string (e.g., output of `openssl rand -hex 32`).
- `OPENAI_API_KEY`: Your valid LLM provider key.
- `CORS_ORIGINS`: Set strictly to the domain of your frontend (e.g., `https://chat.yourdomain.com`). No trailing slashes, no wildcards.

### 3. Deploy
A helper script is provided to automate the build and startup process.

```bash
bash scripts/deploy.sh
```

**What this script does:**
1. Validates that the `.env` file exists.
2. Pulls the latest code via `git`.
3. Runs `docker-compose up -d --build`.
   - The **Backend** will be built and started (mapped to port `8000`). Alembic migrations are automatically handled by the application lifecycle if configured, or you can run them manually (see below).
   - The **Frontend** will be built using a multi-stage Dockerfile that bakes `NEXT_PUBLIC_API_URL` into an ultra-lightweight standalone Node.js container (mapped to port `3000`).
4. Performs a basic health check on the backend.

## Post-Deployment Validation

Check the status of your containers:
```bash
docker-compose ps
```

The backend container should eventually report `(healthy)`. The health check uses the `/health/readiness` endpoint, which verifies database connectivity.

To view logs if something goes wrong:
```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend
```

## Running Database Migrations

If your deployment does not run migrations automatically on startup, you can run them inside the backend container:

```bash
docker-compose exec backend alembic upgrade head
```

## Stopping the Application

```bash
docker-compose down
```

Note: This will not delete your persistent data (SQLite database or Vector store), as they are stored in the mounted `./data` volume.
