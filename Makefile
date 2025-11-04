.PHONY: help build up down restart logs shell clean test

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

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started. Use 'make logs' to view logs."

down:
	docker-compose down

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

