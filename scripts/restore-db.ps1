# ============================================
# MemoryChat — Database Restore Script (PowerShell)
# Restores PostgreSQL running in Docker
# Usage: .\scripts\restore-db.ps1 [-DumpFile .\database\development.sql]
# ============================================

param(
    [string]$DumpFile = "$PSScriptRoot\..\database\development.sql"
)

$ErrorActionPreference = "Stop"
$ProjectDir = (Resolve-Path "$PSScriptRoot\..").Path

# Load .env for POSTGRES_USER, POSTGRES_DB
$EnvFile = Join-Path $ProjectDir ".env"
$POSTGRES_USER = "postgres"
$POSTGRES_DB   = "memorychat"

if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^POSTGRES_USER=(.+)$') { $POSTGRES_USER = $Matches[1] }
        if ($_ -match '^POSTGRES_DB=(.+)$')   { $POSTGRES_DB   = $Matches[1] }
    }
}

if (-not (Test-Path $DumpFile)) {
    Write-Host "❌ Dump file not found: $DumpFile" -ForegroundColor Red
    Write-Host "Usage: .\scripts\restore-db.ps1 -DumpFile <path\to\dump.sql>"
    exit 1
}

Write-Host "⚠️  WARNING: This will DROP all tables and restore from dump!" -ForegroundColor Yellow
Write-Host "   Database: $POSTGRES_DB"
Write-Host "   Dump:     $DumpFile"
Write-Host ""
$Confirm = Read-Host "Continue? (yes/no)"

if ($Confirm -ne "yes") {
    Write-Host "Aborted." -ForegroundColor Gray
    exit 0
}

Set-Location $ProjectDir

Write-Host "🔄 Dropping existing tables..." -ForegroundColor Cyan
docker compose exec -T postgres psql `
    -U $POSTGRES_USER `
    -d $POSTGRES_DB `
    -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" | Out-Null

Write-Host "📦 Restoring from $(Split-Path $DumpFile -Leaf)..." -ForegroundColor Cyan
Get-Content $DumpFile -Raw | docker compose exec -T postgres psql `
    -U $POSTGRES_USER `
    -d $POSTGRES_DB

Write-Host "✅ Database restored successfully!" -ForegroundColor Green
