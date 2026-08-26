.PHONY: help run test lint format typecheck check clean
.PHONY: build run-docker logs shell migrate seed backup restore
.PHONY: docker-build docker-up docker-down docker-restart docker-logs

# ============================================
# MemoryChat Makefile
# ============================================

help: ## Show this help message
	@echo "MemoryChat - Available Commands"
	@echo "=============================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-20s %s\n", $$1, $$2}'

# ---- Development ----
run: ## Run the application locally
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=term-missing

lint: ## Run ruff linter
	ruff check src/ tests/

format: ## Format code with ruff
	ruff format src/ tests/

typecheck: ## Run mypy type checker
	mypy src/

check: lint format test ## Run all checks (lint + format + test)

# ---- Docker ----
docker-build: ## Build Docker image
	docker build -t memorychat:latest .

docker-up: ## Start containers with docker compose
	docker compose up -d

docker-down: ## Stop containers
	docker compose down

docker-restart: ## Restart containers
	docker compose restart

docker-logs: ## Follow docker logs
	docker compose logs -f

# ---- Docker Convenience ----
build: docker-build ## Alias for docker-build
run-docker: docker-up ## Alias for docker-up
logs: docker-logs ## Alias for docker-logs

shell: ## Open shell in running container
	docker compose exec backend bash

ps: ## Show container status
	docker compose ps

# ---- Database ----
migrate: ## Run database migrations
	docker compose exec backend alembic upgrade head

migrate-create: ## Create new migration (Usage: make migrate-create MSG="add column")
	@if [ -z "$(MSG)" ]; then \
		echo "Usage: make migrate-create MSG='description'"; \
		exit 1; \
	fi
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed database with sample data
	PYTHONPATH=. python scripts/seed.py

# ---- Backup & Restore (PostgreSQL) ----
db-backup: ## Backup PostgreSQL → backup/db-TIMESTAMP.sql
	@mkdir -p backup
	docker compose exec -T postgres pg_dump -U $${POSTGRES_USER:-postgres} -d $${POSTGRES_DB:-memorychat} --no-owner --no-acl > backup/db-$$(date +%Y%m%d-%H%M%S).sql
	@echo "✅ Backup saved to ./backup/"

db-restore: ## Restore PostgreSQL from dump (Usage: make db-restore FILE=backup/db-XXX.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make db-restore FILE=<path/to/dump.sql>"; \
		echo "Available backups:"; \
		ls -la backup/*.sql 2>/dev/null || echo "No SQL backups found"; \
		exit 1; \
	fi
	docker compose exec -T postgres psql -U $${POSTGRES_USER:-postgres} -d $${POSTGRES_DB:-memorychat} -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	docker compose exec -T postgres psql -U $${POSTGRES_USER:-postgres} -d $${POSTGRES_DB:-memorychat} < $(FILE)
	@echo "✅ Database restored from $(FILE)"

db-dump: ## Update database/development.sql from running PostgreSQL (overwrites!)
	@mkdir -p database
	docker compose exec -T postgres pg_dump -U $${POSTGRES_USER:-postgres} -d $${POSTGRES_DB:-memorychat} --no-owner --no-acl > database/development.sql
	@echo "✅ database/development.sql updated"

db-reset: ## ⚠️  DANGER: Drop and re-init database from development.sql
	@echo "⚠️  WARNING: This will erase all data and restore from database/development.sql!"
	@read -p "Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker compose exec -T postgres psql -U $${POSTGRES_USER:-postgres} -d $${POSTGRES_DB:-memorychat} -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"; \
		docker compose exec -T postgres psql -U $${POSTGRES_USER:-postgres} -d $${POSTGRES_DB:-memorychat} < database/development.sql; \
		echo "✅ Database reset complete."; \
	else \
		echo "Aborted."; \
	fi

backup: db-backup ## Alias for db-backup
restore: ## Restore from backup — use: make db-restore FILE=<path>
	@echo "Use: make db-restore FILE=<path/to/dump.sql>"

# ---- Utility ----
clean: ## Clean cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .coverage htmlcov/ 2>/dev/null || true

clean-all: clean ## Clean everything including data
	rm -rf data/ .ai-log/ backup/ 2>/dev/null || true
	docker compose down -v 2>/dev/null || true

# ---- Health Check ----
health: ## Check if service is healthy
	@curl -s http://localhost:8000/health | python -m json.tool || echo "Service not responding"

# ---- Development Helpers ----
dev-setup: ## Setup development environment
	pip install -r requirements.txt
	cp .env.example .env

lint-fix: ## Auto-fix linting issues
	ruff check --fix src/ tests/
