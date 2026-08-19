# Disaster Recovery & Rollback Plan

This document outlines the standard procedures for rolling back deployments and recovering from critical failures in Production.

## 1. Application Rollback (Docker)

If a new deployment introduces critical bugs that cannot be hotfixed immediately, rollback to the previous known good Docker image.

### Frontend / Backend Rollback
Assuming you tag your Docker images (e.g., `memorychat-backend:v1.0.0`):
1. Identify the previous stable image tag.
2. Edit `docker-compose.yml` (if using explicit tags) or simply revert the Git commit that triggered the bad deployment.
```bash
git revert HEAD
# or checkout a specific stable tag
git checkout v1.0.0
```
3. Re-deploy the containers:
```bash
bash scripts/deploy.sh
```

## 2. Database Rollback

**CRITICAL RULE:** Do not deploy a database migration that cannot be safely handled during a rollback. Prefer backward-compatible migrations (e.g., add a new field, deploy backend, migrate data, start using the field).

### Reverting Alembic Migrations
If a migration causes issues and needs to be undone:
1. Shell into the backend container:
```bash
docker-compose exec backend bash
```
2. Downgrade the database by one revision:
```bash
alembic downgrade -1
```
*(Or specify a specific revision ID to downgrade to).*

### SQLite Backup & Restore
Since we currently use SQLite mounted via Docker volumes, backups are file-based.

**To Backup (Automate this via cron):**
```bash
# Safely copy the SQLite database file
sqlite3 ./data/memorychat.db ".backup './data/backup_$(date +%F).db'"
```

**To Restore:**
1. Stop the backend container to prevent writes:
```bash
docker-compose stop backend
```
2. Replace the active database with the backup:
```bash
cp ./data/backup_YYYY-MM-DD.db ./data/memorychat.db
```
3. Restart the backend:
```bash
docker-compose start backend
```

## 3. AI Feature Fail-safes

If the LLM provider (OpenAI/Anthropic) goes down, or if the AI Workers are causing memory leaks / excessive billing:

1. **Disable AI Workers**: Scale the specific AI worker containers to 0 (if separated) or use environment toggles if built into the monolith.
2. **Graceful Degradation**: The system is designed to fall back to basic PostgreSQL/SQLite ILIKE search if VectorDB/LLM fails (implemented in Phase 12).
3. **Purge AI Queues**: If the `OutboxWorker` is clogged with failing AI jobs, you may need to manually clear the queued tasks in the database to restore standard message delivery throughput.
