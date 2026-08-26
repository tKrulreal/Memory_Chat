#!/bin/bash
# ============================================
# MemoryChat Restore Script
# Usage: ./scripts/restore.sh <backup_file> [--dry-run]
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backup"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

show_usage() {
    echo "Usage: $0 <backup_file> [--dry-run]"
    echo ""
    echo "Arguments:"
    echo "  backup_file    Path to the backup archive (.tar.gz)"
    echo "  --dry-run      Show what would be restored without actually restoring"
    echo ""
    echo "Examples:"
    echo "  $0 backup/data-20240101-120000.tar.gz"
    echo "  $0 backup/latest.tar.gz"
    echo "  $0 backup/latest.tar.gz --dry-run"
}

# Check arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No backup file specified${NC}"
    show_usage
    exit 1
fi

BACKUP_FILE="$1"
DRY_RUN=false

if [ "$2" = "--dry-run" ]; then
    DRY_RUN=true
    echo -e "${YELLOW}🔍 DRY RUN MODE - No changes will be made${NC}"
    echo ""
fi

# Resolve backup file path
if [ ! -f "$BACKUP_FILE" ]; then
    # Try relative to backup directory
    if [ -f "$BACKUP_DIR/$(basename "$BACKUP_FILE")" ]; then
        BACKUP_FILE="$BACKUP_DIR/$(basename "$BACKUP_FILE")"
    else
        echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
        echo ""
        echo "Available backups:"
        ls -la "$BACKUP_DIR/" 2>/dev/null || echo "No backups found"
        exit 1
    fi
fi

echo "📥 Restore Backup"
echo "   Backup file: $BACKUP_FILE"

# Show backup info
if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    BACKUP_DATE=$(date -r "$BACKUP_FILE" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "unknown")
    echo "   Size: $BACKUP_SIZE"
    echo "   Created: $BACKUP_DATE"
fi

echo ""

# Change to project directory
cd "$PROJECT_DIR"

# Dry run - list contents
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}📋 Backup contents:${NC}"
    tar -tzf "$BACKUP_FILE" | head -50
    echo "   ... (truncated)"
    echo ""
    echo -e "${GREEN}✅ Dry run complete. No changes were made.${NC}"
    exit 0
fi

# Confirm before restoring
echo -e "${YELLOW}⚠️  WARNING: This will overwrite current data!${NC}"
echo ""
read -p "Are you sure you want to restore? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restore cancelled."
    exit 0
fi

# Stop services if running (for Docker)
if docker compose ps 2>/dev/null | grep -q "Up"; then
    echo "Stopping services..."
    docker compose down 2>/dev/null || true
fi

# Backup current data before restoring
if [ -d "data" ] || [ -d ".ai-log" ]; then
    echo "📦 Backing up current data..."
    CURRENT_BACKUP="backup/pre-restore-$(date +%Y%m%d-%H%M%S).tar.gz"
    mkdir -p backup
    tar -czf "$CURRENT_BACKUP" ./data/ ./.ai-log/ 2>/dev/null || true
    echo "   Current data backed up to: $CURRENT_BACKUP"
fi

# Remove current data
echo "🗑️  Removing current data..."
rm -rf data/ .ai-log/
mkdir -p data/ .ai-log/

# Extract backup
echo "📂 Extracting backup..."
tar -xzf "$BACKUP_FILE"

echo ""
echo -e "${GREEN}✅ Restore completed successfully!${NC}"
echo ""
echo "📋 Restored files:"
ls -la data/ .ai-log/ 2>/dev/null || true
echo ""
echo "To restart services: make docker-up"
