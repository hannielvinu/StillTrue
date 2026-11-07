.PHONY: install dev test lint build up bench record-demo
install:
	cd backend && UV_CACHE_DIR=/tmp/stilltrue-uv uv sync --frozen
	cd frontend && npm ci --cache /tmp/stilltrue-npm
dev:
	bash scripts/dev.sh
test:
	cd backend && .venv/bin/pytest -q
	cd frontend && npm test
lint:
	backend/.venv/bin/ruff check backend scripts benchmark
	backend/.venv/bin/ruff format --check backend scripts benchmark
	cd frontend && npm run typecheck
build:
	cd frontend && npm run build
up:
	docker compose up --build -d
bench:
	cd backend && .venv/bin/python ../benchmark/run_benchmark.py
record-demo:
	cd backend && .venv/bin/python ../scripts/record_demo_run.py $(CAPTURE)
