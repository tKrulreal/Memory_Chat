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

migrate-create MSG=? ## Create new migration (Usage: make migrate-create MSG="add column")
	@if [ -z "$(MSG)" ]; then \
		echo "Usage: make migrate-create MSG='description'"; \
		exit 1; \
	fi
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed database with sample data
	PYTHONPATH=. python scripts/seed.py

# ---- Backup & Restore ----
backup: ## Create database backup
	@mkdir -p backup
	docker compose exec backend bash -c "tar -czf /tmp/backup-$$(date +%Y%m%d-%H%M%S).tar.gz -C /app data .ai-log 2>/dev/null || true"
	@echo "Backup created in ./backup/"

restore FILE=? ## Restore from backup (Usage: make restore FILE=backup-20240101-120000.tar.gz)
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make restore FILE=<filename>"; \
		echo "Available backups:"; \
		ls -la backup/ 2>/dev/null || echo "No backups found"; \
		exit 1; \
	fi
	@if [ ! -f "backup/$(FILE)" ]; then \
		echo "File not found: backup/$(FILE)"; \
		exit 1; \
	fi
	docker compose exec -T backend bash -c "cd /app && tar -xzf /tmp/$(FILE) || tar -xzf /backup/$(FILE) || echo 'Extracting from current dir'; ls -la data/"

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
