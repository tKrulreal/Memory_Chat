# ============================================
# MemoryChat — Database Backup Script (PowerShell)
# Backs up PostgreSQL running in Docker
# Usage: .\scripts\backup-db.ps1 [-OutputDir .\backup]
# ============================================

param(
    [string]$OutputDir = "$PSScriptRoot\..\backup"
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

# Ensure backup directory exists
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$Timestamp  = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupFile = Join-Path $OutputDir "db-$Timestamp.sql"

Write-Host "🚀 Starting PostgreSQL backup..." -ForegroundColor Cyan
Write-Host "   Database: $POSTGRES_DB"
Write-Host "   Output:   $BackupFile"

Set-Location $ProjectDir

docker compose exec -T postgres pg_dump `
    -U $POSTGRES_USER `
    -d $POSTGRES_DB `
    --no-owner `
    --no-acl `
    | Out-File -FilePath $BackupFile -Encoding UTF8

if (Test-Path $BackupFile) {
    $Size = (Get-Item $BackupFile).Length
    $SizeKB = [math]::Round($Size / 1KB, 1)
    Write-Host "✅ Backup created: $BackupFile ($SizeKB KB)" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 To restore:" -ForegroundColor Yellow
    Write-Host "   .\scripts\restore-db.ps1 -DumpFile '$BackupFile'"
} else {
    Write-Host "❌ Backup failed!" -ForegroundColor Red
    exit 1
}
