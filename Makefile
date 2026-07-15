.PHONY: install dev test lint build docker-up docker-down
install:
	python3.12 -m venv .venv && .venv/bin/pip install -r apps/api/requirements-dev.txt
	cd apps/web && pnpm install
dev:
	@echo "Run API: .venv/bin/uvicorn apps.api.main:app --reload --port 8000"
	@echo "Run web: cd apps/web && pnpm dev"
test:
	.venv/bin/pytest
	cd apps/web && pnpm test
lint:
	.venv/bin/ruff check apps packages tests
	.venv/bin/mypy apps packages
	cd apps/web && pnpm lint && pnpm typecheck
build:
	cd apps/web && pnpm build
	docker build -f apps/api/Dockerfile -t marketlens-api:local .
	docker build -f apps/web/Dockerfile -t marketlens-web:local .
docker-up:
	docker compose up --build -d
docker-down:
	docker compose down
