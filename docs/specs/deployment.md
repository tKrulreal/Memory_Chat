# DEPLOYMENT.md — Infrastructure & Deployment

## MemoryChat MVP v1.0

---

## 1. Deployment Overview

### 1.1 Deployment Strategy

MemoryChat uses a **progressive deployment strategy** that prioritizes simplicity for MVP while maintaining a production-ready architecture:

```
MVP (Week 1-6)
    │
    └── Single Docker Container
            │
            ├── FastAPI + Uvicorn
            ├── SQLite + ChromaDB
            └── asyncio Workers

    ▼

Phase 2 (Post-MVP)
    │
    └── Docker Compose
            │
            ├── Backend API (multiple instances)
            ├── PostgreSQL
            ├── Qdrant
            ├── Redis
            └── Celery Workers

    ▼

Phase 3 (Scale)
    │
    └── Kubernetes
            │
            ├── Load Balancer
            ├── Multiple API Pods
            ├── PostgreSQL Cluster
            ├── Qdrant Cluster
            ├── Neo4j Cluster
            └── Redis Cluster
```

### 1.2 Environment Overview

| Environment | Purpose | URL |
|-------------|---------|-----|
| Local | Development | `http://localhost:8000` |
| Staging | Testing | `https://api.staging.memorychat.vn` |
| Production | Live users | `https://api.memorychat.vn` |

---

## 2. MVP Deployment

### 2.1 Local Development

```bash
# Clone repository
git clone https://github.com/your-org/memorychat.git
cd memorychat

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
# OPENAI_API_KEY=sk-...

# Run with Docker
docker-compose up --build

# Or run locally
make run
```

### 2.2 Docker Setup (MVP)

```yaml
# docker-compose.yml (MVP)
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    env_file:
      - .env
    environment:
      - DATABASE_URL=sqlite:///./data/app.db
      - CHROMA_PERSIST_DIR=/app/data/chroma
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```dockerfile
# Dockerfile (MVP)
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.3 Makefile Commands

```makefile
# Makefile
.PHONY: run build test clean docker-up docker-down

run:
	python -m uvicorn src.main:app --reload --port 8000

build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	pytest tests/ -v

clean:
	rm -rf data/*.db data/chroma/*
```

---

## 3. Phase 2 Deployment (Docker Compose)

### 3.1 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Compose                             │
│                                                                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐         │
│  │   Nginx     │   │  Backend 1  │   │  Backend 2  │         │
│  │  (Reverse   │──►│  (FastAPI)  │   │  (FastAPI)  │         │
│  │   Proxy)    │   └─────────────┘   └─────────────┘         │
│  └─────────────┘          │                   │                 │
│                           │                   │                 │
│  ┌─────────────┐   ┌─────┴─────────┐   ┌────┴────────┐      │
│  │   Celery    │   │   PostgreSQL  │   │   Qdrant    │      │
│  │   Worker    │   │               │   │             │      │
│  └─────────────┘   └───────────────┘   └─────────────┘      │
│         │                                                           │
│  ┌─────────────┐                                                 │
│  │   Redis     │                                                 │
│  │ (Broker)    │                                                 │
│  └─────────────┘                                                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Docker Compose (Phase 2)

```yaml
# docker-compose.yml (Phase 2)
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend-1
      - backend-2
    networks:
      - backend-network

  backend-1:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/memorychat
      - REDIS_URL=redis://redis:6379
      - CHROMA_PERSIST_DIR=/app/data/chroma
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - backend-network
    deploy:
      replicas: 2

  backend-2:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/memorychat
      - REDIS_URL=redis://redis:6379
      - CHROMA_PERSIST_DIR=/app/data/chroma
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - backend-network

  worker-memory:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A src.workers.memory worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/memorychat
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - postgres
    networks:
      - backend-network

  worker-recommendation:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A src.workers.recommendation worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/memorychat
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - postgres
    networks:
      - backend-network

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: memorychat
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d memorychat"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend-network

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend-network

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant-data:/qdrant/storage
    networks:
      - backend-network

volumes:
  postgres-data:
  redis-data:
  qdrant-data:

networks:
  backend-network:
    driver: bridge
```

### 3.3 Nginx Configuration

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        least_conn;
        server backend-1:8000;
        server backend-2:8000;
    }

    server {
        listen 80;
        server_name api.memorychat.vn;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.memorychat.vn;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Rate limiting
        limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
        limit_req_zone $binary_remote_addr zone=copilot:10m rate=2r/s;

        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api/v1/copilot {
            limit_req zone=copilot burst=5 nodelay;
            proxy_pass http://backend;
            # ... same headers
        }

        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            # ... same headers
        }
    }
}
```

---

## 4. CI/CD Pipeline

### 4.1 GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # Job 1: Run Tests
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest tests/ -v --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  # Job 2: Build Docker Image
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # Job 3: Deploy to Staging
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    steps:
      - name: Deploy to staging
        run: |
          # SSH to staging server and pull new image
          ssh ${{ secrets.STAGING_HOST }} "
            docker pull ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:develop
            docker-compose -f /app/memorychat/docker-compose.staging.yml up -d
          "

  # Job 4: Deploy to Production
  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - name: Deploy to production
        run: |
          # Blue-green deployment
          ssh ${{ secrets.PRODUCTION_HOST }} "
            docker-compose -f /app/memorychat/docker-compose.prod.yml exec backend-1 python -m alembic upgrade head
            docker-compose -f /app/memorychat/docker-compose.prod.yml restart backend-1 backend-2
          "
```

### 4.2 Deployment Checklist

```markdown
## Pre-Deployment Checklist

### Code
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] No security vulnerabilities
- [ ] Environment variables configured
- [ ] Database migrations ready

### Infrastructure
- [ ] Servers accessible
- [ ] Docker images built
- [ ] Databases backed up
- [ ] Monitoring dashboards ready

### Communication
- [ ] Team notified of deployment
- [ ] Rollback plan documented
- [ ] On-call engineer available

## Post-Deployment Checklist

### Verification
- [ ] Health check passing
- [ ] Key features working
- [ ] No increase in error rate
- [ ] Performance metrics normal

### Monitoring
- [ ] Check dashboards
- [ ] Check logs for errors
- [ ] Monitor error rates
- [ ] Monitor latency
```

---

## 5. Environment Configuration

### 5.1 Environment Variables

```bash
# .env.example

# ===================
# Application
# ===================
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=true

# ===================
# OpenAI (Required)
# ===================
OPENAI_API_KEY=sk-your-api-key
MODEL_NAME=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# ===================
# Database
# ===================
# SQLite (MVP)
DATABASE_URL=sqlite:///./data/app.db

# PostgreSQL (Production)
# DATABASE_URL=postgresql://user:password@localhost:5432/memorychat

# ===================
# ChromaDB / Qdrant
# ===================
CHROMA_PERSIST_DIR=./data/chroma
# QDRANT_URL=http://localhost:6333

# ===================
# Redis
# ===================
REDIS_URL=redis://localhost:6379/0

# ===================
# JWT (Production)
# ===================
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ===================
# CORS
# ===================
CORS_ORIGINS=http://localhost:3000,https://memorychat.vn

# ===================
# Optional Services
# ===================
# SENTRY_DSN=https://example@sentry.io/123
# LANGCHAIN_API_KEY=...
# LANGCHAIN_TRACING_V2=true
```

### 5.2 Secret Management

```bash
# Production secrets should be managed via environment-specific files

# /secrets/production.env (never commit this)
OPENAI_API_KEY=sk-prod-...
JWT_SECRET=prod-secret-key
DATABASE_URL=postgresql://prod-user:prod-pass@prod-host:5432/memorychat
```

---

## 6. Monitoring & Observability

### 6.1 Application Metrics (MVP)

```python
# src/core/monitoring.py
from prometheus_client import Counter, Histogram, generate_latest

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# AI metrics
LLM_CALLS = Counter(
    'llm_calls_total',
    'Total LLM calls',
    ['model', 'type']
)

LLM_LATENCY = Histogram(
    'llm_call_duration_seconds',
    'LLM call latency',
    ['model']
)

LLM_TOKEN_USAGE = Counter(
    'llm_tokens_total',
    'Total LLM tokens used',
    ['model', 'type']
)

# Database metrics
DB_QUERY_LATENCY = Histogram(
    'db_query_duration_seconds',
    'Database query latency',
    ['operation']
)
```

### 6.2 Logging Configuration

```python
# src/core/logging.py
import logging
import sys
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['service'] = 'memorychat-backend'
        log_record['environment'] = os.getenv('ENVIRONMENT', 'development')

# Configure logging
def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler]
    )
    
    # Set specific loggers
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    logging.getLogger('aiogram').setLevel(logging.WARNING)
```

### 6.3 Health Check Endpoint

```python
# src/api/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/ready")
async def readiness_check():
    # Check all dependencies
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "chroma": await check_chroma(),
    }
    
    all_healthy = all(checks.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks
    }
```

---

## 7. Backup & Recovery

### 7.1 Backup Strategy

```bash
#!/bin/bash
# scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/memorychat
mkdir -p $BACKUP_DIR

# Backup SQLite database
cp ./data/app.db $BACKUP_DIR/app.db.$DATE

# Backup ChromaDB
tar -czf $BACKUP_DIR/chroma.$DATE.tar.gz ./data/chroma

# Keep only last 7 days
find $BACKUP_DIR -mtime +7 -delete

echo "Backup completed: $DATE"
```

### 7.2 Restore Procedure

```bash
#!/bin/bash
# scripts/restore.sh

DATE=$1
BACKUP_DIR=/backups/memorychat

if [ -z "$DATE" ]; then
    echo "Usage: $0 <backup-date>"
    exit 1
fi

# Stop application
docker-compose down

# Restore database
cp $BACKUP_DIR/app.db.$DATE ./data/app.db

# Restore ChromaDB
tar -xzf $BACKUP_DIR/chroma.$DATE.tar.gz -C ./

# Start application
docker-compose up -d

echo "Restore completed for: $DATE"
```

---

## 8. Security

### 8.1 Security Checklist

```markdown
## Security Checklist

### Authentication
- [x] JWT tokens with expiration
- [ ] Refresh token rotation
- [ ] Rate limiting on auth endpoints
- [ ] Account lockout after failed attempts

### Authorization
- [x] User can only access own data
- [ ] Role-based access control (RBAC)
- [ ] API key authentication for services

### Data Protection
- [x] Password hashing (bcrypt)
- [x] SQL injection prevention (ORM)
- [ ] Encryption at rest
- [x] HTTPS only
- [ ] PII data masking

### API Security
- [x] Input validation (Pydantic)
- [ ] Rate limiting
- [ ] CORS configuration
- [ ] API versioning

### AI Security
- [ ] Prompt injection detection
- [ ] Output filtering
- [ ] Data leakage prevention
- [ ] Context isolation
```

### 8.2 CORS Configuration

```python
# src/core/middleware.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://memorychat.vn",   # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 9. Scaling

### 9.1 Horizontal Scaling

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: memorychat-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: memorychat-backend
  template:
    metadata:
      labels:
        app: memorychat-backend
    spec:
      containers:
      - name: backend
        image: ghcr.io/your-org/memorychat:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        env:
          - name: DATABASE_URL
            valueFrom:
              secretKeyRef:
                name: memorychat-secrets
                key: database-url
---
apiVersion: v1
kind: Service
metadata:
  name: memorychat-backend
spec:
  selector:
    app: memorychat-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 9.2 Database Scaling

```sql
-- Read replica setup (PostgreSQL)
-- Primary handles writes, replicas handle reads

-- Application can route reads to replicas
-- Connection pool for better performance
-- Partitioning for large tables (messages)
```

---

## 10. Disaster Recovery

### 10.1 Recovery Procedures

```markdown
## Recovery Time Objectives (RTO)

| Service | RTO | RPO |
|---------|-----|-----|
| API | 15 min | 5 min |
| Database | 1 hour | 1 hour |
| Vector DB | 1 hour | 1 hour |

## Recovery Procedures

### Complete Outage
1. Verify infrastructure status
2. Check monitoring dashboards
3. Identify root cause
4. Execute recovery plan
5. Verify service health
6. Post-mortem analysis

### Database Failure
1. Promote read replica (if available)
2. Restore from latest backup
3. Verify data integrity
4. Resume operations

### Application Failure
1. Check container logs
2. Restart failed containers
3. Scale up if needed
4. Verify health checks
```

### 10.2 Runbooks

```markdown
## Runbook: High API Latency

### Symptoms
- API response time > 2 seconds
- User complaints about slowness

### Investigation
1. Check database query times
2. Check LLM API response times
3. Check Redis cache hit rate
4. Check for slow queries

### Resolution
1. Scale up backend instances
2. Enable caching if not active
3. Optimize slow queries
4. Consider circuit breaker

## Runbook: LLM API Errors

### Symptoms
- High error rate on AI endpoints
- "AI is unavailable" errors

### Investigation
1. Check OpenAI API status
2. Check API key validity
3. Check rate limits

### Resolution
1. Enable fallback model
2. Queue requests for retry
3. Notify users of delays
```

---

## 11. Cost Optimization

### 11.1 Cost Breakdown (MVP)

| Component | Monthly Cost |
|-----------|-------------|
| Compute (local) | $0 |
| Database (SQLite) | $0 |
| Vector DB (ChromaDB) | $0 |
| LLM API (gpt-4o-mini) | ~$5-20 |
| Monitoring | $0 |
| **Total MVP** | **~$5-20/month** |

### 11.2 Cost Optimization Strategies

| Strategy | Implementation | Savings |
|---------|---------------|---------|
| Use smaller models | gpt-4o-mini for most tasks | 80-90% |
| Batch processing | Group messages before LLM call | 50-70% |
| Caching | Cache frequent queries | 30-50% |
| Rate limiting | Prevent abuse | N/A |
| Reserved capacity | Prepay for resources | 20-40% |

---

## 12. Infrastructure as Code

### 12.1 Project Structure

```
infrastructure/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── modules/
│   │   ├── vpc/
│   │   ├── ecs/
│   │   ├── rds/
│   │   └── redis/
│   └── environments/
│       ├── staging/
│       └── production/
├── ansible/
│   ├── playbook.yml
│   ├── roles/
│   │   ├── docker/
│   │   ├── nginx/
│   │   └── monitoring/
│   └── inventory/
└── kubernetes/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    └── configmap.yaml
```

---

*Document Version: 1.0*  
*Last Updated: 2026-08-13*
