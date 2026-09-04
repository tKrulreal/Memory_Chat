# CI/CD Pipeline Documentation

## Overview

This project uses GitHub Actions for CI/CD with multiple workflows for different purposes.

## Workflows

### 1. Main CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

**Triggers:**
- Push to `main` or `develop` branch
- Pull requests to `main`

**Jobs:**
1. **Lint & Type Check** - Code quality validation
   - Python: Ruff linting
   - Frontend: ESLint + TypeScript check

2. **Backend Tests** - Python unit/integration tests
   - PostgreSQL service
   - Coverage reports
   - Alembic migration tests

3. **Frontend Build** - Next.js build validation
   - TypeScript compilation
   - Production build test

4. **Database Migrations** - Migration validation
   - Upgrade to latest
   - Verify migration state

5. **Docker Build** (main branch only)
   - Build backend image
   - Build frontend image
   - Push to GitHub Container Registry

6. **Deploy to Production** (main branch only)
   - Deploy via Docker Compose
   - Health check verification

7. **Security Scan**
   - Trivy vulnerability scanning
   - Python dependency audit (Safety)

### 2. Develop Branch CI (`.github/workflows/develop.yml`)

**Triggers:**
- Push to `develop` branch
- Pull requests to `develop`

**Purpose:** Quick validation without full deployment

### 3. Preview Deployment (`.github/workflows/preview.yml`)

**Triggers:**
- Pull requests (opened, synchronize, reopened)

**Purpose:**
- Build preview Docker images
- Deploy preview environment
- Comment PR with preview URL
- Cleanup on PR close

### 4. Nightly Build (`.github/workflows/nightly.yml`)

**Triggers:**
- Daily at 2 AM UTC
- Manual dispatch

**Purpose:**
- Full integration tests
- Docker build verification
- Dependency audit

## Required Secrets

Configure these in GitHub repository settings:

| Secret | Description | Required |
|--------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `QDRANT_URL` | Qdrant vector store URL | Yes |
| `PRODUCTION_DATABASE_URL` | Production PostgreSQL URL | For deploy |
| `RAILWAY_TOKEN` | Railway deployment token | For Railway deploy |
| `RAILWAY_PROJECT_ID` | Railway project ID | For Railway deploy |
| `DOCKER_HOST` | Docker socket for deploy | For Docker deploy |
| `SAFETY_API_KEY` | PyUp Safety API key | Optional |

## Required Variables

Configure these in GitHub repository settings → Variables:

| Variable | Description |
|----------|-------------|
| `FRONTEND_API_URL` | Production API URL for frontend build |

## Local Development

### Run CI/CD checks locally

```bash
# Backend tests
docker compose up -d postgres
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/memorychat
alembic upgrade head
pytest tests/ -v

# Frontend build
cd frontend
npm ci
npm run build

# Docker build test
docker build -t memorychat-backend .
docker build -t memorychat-frontend ./frontend
```

### Production deployment

```bash
# Using Docker Compose
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Using Railway
railway login
railway init
railway up
```

## Docker Images

Images are stored in GitHub Container Registry:
- Backend: `ghcr.io/ai20k-build-phase-cohort-3/p-214/backend`
- Frontend: `ghcr.io/ai20k-build-phase-cohort-3/p-214/frontend`

## Branch Strategy

```
main        → Production deployment
develop     → Pre-production testing
PR branches → Preview deployments
```

## Status Badges

Add these badges to your README:

```markdown
[![CI/CD](https://github.com/ai20k-build-phase-cohort-3/p-214/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/ai20k-build-phase-cohort-3/p-214/actions/workflows/ci-cd.yml)
```
