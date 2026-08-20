#!/bin/bash
# ============================================
# MemoryChat — PostgreSQL Initialization Script
# Runs automatically on first container start
# (only when the volume is empty / brand new)
# ============================================
set -e

echo "🔄 [init] Checking if database needs initialization..."

# Check if tables already exist (idempotent guard)
TABLE_COUNT=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc \
  "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null || echo "0")

if [ "$TABLE_COUNT" -gt "0" ]; then
  echo "✅ [init] Database already has $TABLE_COUNT tables — skipping restore."
  exit 0
fi

DUMP_FILE="/docker-entrypoint-initdb.d/development.sql"

if [ -f "$DUMP_FILE" ]; then
  echo "📦 [init] Restoring development database from dump..."
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < "$DUMP_FILE"
  echo "✅ [init] Database restored successfully!"
else
  echo "⚠️  [init] No dump file found at $DUMP_FILE — starting with empty database."
  echo "    Run 'make db-restore' to restore manually."
fi
