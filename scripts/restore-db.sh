#!/bin/bash
# ============================================
# MemoryChat — Database Restore Script
# Restores PostgreSQL running in Docker
# Usage: ./scripts/restore-db.sh <dump_file>
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env if it exists
if [ -f "$PROJECT_DIR/.env" ]; then
  set -a
  source "$PROJECT_DIR/.env"
  set +a
fi

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-memorychat}"
DUMP_FILE="${1:-$PROJECT_DIR/database/development.sql}"

if [ ! -f "$DUMP_FILE" ]; then
  echo "❌ Dump file not found: $DUMP_FILE"
  echo "Usage: ./scripts/restore-db.sh [path/to/dump.sql]"
  exit 1
fi

echo "⚠️  WARNING: This will DROP all tables and restore from dump!"
echo "   Database: $POSTGRES_DB"
echo "   Dump:     $DUMP_FILE"
echo ""
read -p "Continue? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

cd "$PROJECT_DIR"

echo "🔄 Dropping existing tables..."
docker compose exec -T postgres psql \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" \
  > /dev/null

echo "📦 Restoring from $DUMP_FILE ..."
docker compose exec -T postgres psql \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  < "$DUMP_FILE"

echo "✅ Database restored successfully from $(basename "$DUMP_FILE")!"
