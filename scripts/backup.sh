#!/bin/bash
# ============================================
# MemoryChat Backup Script
# Usage: ./scripts/backup.sh [output_dir]
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${1:-$PROJECT_DIR/backup}"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/data-$TIMESTAMP.tar.gz"

echo "🚀 Starting backup..."
echo "   Backup directory: $BACKUP_DIR"
echo "   Output file: $BACKUP_FILE"

# Change to project directory
cd "$PROJECT_DIR"

# Create backup of data directory (SQLite + ChromaDB)
if [ -d "data" ]; then
    echo "📦 Backing up ./data/..."
    DATA_SIZE=$(du -sh data 2>/dev/null | cut -f1 || echo "unknown")
    echo "   Size: $DATA_SIZE"
fi

# Create backup of AI logs
if [ -d ".ai-log" ]; then
    echo "📝 Backing up ./.ai-log/..."
fi

# Create tar archive
tar -czf "$BACKUP_FILE" \
    --exclude='data/chroma/*.log' \
    --exclude='data/*.db-shm' \
    --exclude='data/*.db-wal' \
    ./data/ \
    ./.ai-log/ \
    2>/dev/null || true

# Verify backup was created
if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✅ Backup created successfully!"
    echo "   File: $BACKUP_FILE"
    echo "   Size: $BACKUP_SIZE"

    # Create latest symlink
    ln -sf "$(basename "$BACKUP_FILE")" "$BACKUP_DIR/latest.tar.gz"

    echo ""
    echo "📋 To restore:"
    echo "   ./scripts/restore.sh $BACKUP_DIR/$(basename $BACKUP_FILE)"
else
    echo "❌ Backup failed!"
    exit 1
fi
