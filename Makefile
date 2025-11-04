.PHONY: help build up down restart logs shell clean test migrate upgrade revision smoke fmt lint

help:
	@echo "AutoSub Bot - Available commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make restart  - Restart all services"
	@echo "  make logs     - Show logs"
	@echo "  make shell    - Open shell in bot container"
	@echo "  make clean    - Clean storage and temp files"
	@echo "  make test     - Run tests"
	@echo "  make backup   - Backup database"
	@echo "  make migrate  - Run database migrations"
	@echo "  make upgrade  - Upgrade database to head"
	@echo "  make revision - Create new migration (use: make revision m='description')"
	@echo "  make smoke    - Run smoke tests"
	@echo "  make fmt      - Format code with black"
	@echo "  make lint     - Lint code with flake8"

build:
	docker-compose build

up:
	docker-compose up -d --build
	@echo "Services started. Use 'make logs' to view logs."

down:
	docker-compose down -v

migrate:
	docker-compose exec bot alembic upgrade head || true
	@echo "DB migrated"

upgrade:
	docker-compose exec bot alembic upgrade head

revision:
	docker-compose exec bot alembic revision -m "$(m)" --autogenerate

smoke:
	bash scripts/smoke.sh

fmt:
	black .

lint:
	flake8 .

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec bot /bin/bash

clean:
	python scripts/cleanup_storage.py

test:
	pytest tests/ -v

backup:
	./scripts/backup_db.sh

# Local development
dev-setup:
	python -m venv venv
	./venv/bin/pip install -r requirements.txt
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

dev-run-bot:
	python -m bot.main

dev-run-worker:
	python -m worker.main

dev-init-db:
	python scripts/init_db.py

