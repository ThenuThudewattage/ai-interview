.PHONY: dev stop backend frontend migrate seed test lint format

# ── Local Development ─────────────────────────────────────────
dev:
	docker-compose up -d postgres redis
	@echo "⏳ Waiting for DB..."
	@sleep 3
	$(MAKE) migrate
	@echo "✅ Infrastructure ready. Run 'make backend' and 'make frontend' in separate terminals."

stop:
	docker-compose down

# ── Individual Services ───────────────────────────────────────
backend:
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && ng serve

# ── Database ──────────────────────────────────────────────────
migrate:
	cd backend && alembic upgrade head

migrate-create:
	cd backend && alembic revision --autogenerate -m "$(msg)"

seed:
	cd backend && python scripts/seed_database.py

# ── Testing ───────────────────────────────────────────────────
test-backend:
	cd backend && python -m pytest tests/ -v

test-frontend:
	cd frontend && ng test --watch=false

test:
	$(MAKE) test-backend
	$(MAKE) test-frontend

# ── Code Quality ──────────────────────────────────────────────
lint:
	cd backend && ruff check app/
	cd frontend && ng lint

format:
	cd backend && black app/ && ruff check --fix app/

type-check:
	cd backend && mypy app/

# ── Docker ────────────────────────────────────────────────────
docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down -v

# ── Helpers ───────────────────────────────────────────────────
install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

setup: install-backend install-frontend
	@echo "✅ Dependencies installed"
