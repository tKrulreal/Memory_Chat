#!/bin/bash
# ============================================
# MemoryChat — Database Backup Script
# Backs up PostgreSQL running in Docker
# Usage: ./scripts/backup-db.sh [output_dir]
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${1:-$PROJECT_DIR/backup}"

# Load .env if it exists (to get POSTGRES_USER, POSTGRES_DB, etc.)
if [ -f "$PROJECT_DIR/.env" ]; then
  set -a
  source "$PROJECT_DIR/.env"
  set +a
fi

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-memorychat}"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db-$TIMESTAMP.sql"

echo "🚀 Starting PostgreSQL backup..."
echo "   Database: $POSTGRES_DB"
echo "   Output:   $BACKUP_FILE"

cd "$PROJECT_DIR"

# Dump using pg_dump inside container — never exposes password in command line
docker compose exec -T postgres pg_dump \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  --no-owner \
  --no-acl \
  > "$BACKUP_FILE"

if [ -f "$BACKUP_FILE" ]; then
  BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  echo "✅ Backup created: $BACKUP_FILE ($BACKUP_SIZE)"
  echo ""
  echo "📋 To restore:"
  echo "   ./scripts/restore-db.sh $BACKUP_FILE"
else
  echo "❌ Backup failed!"
  exit 1
fi
