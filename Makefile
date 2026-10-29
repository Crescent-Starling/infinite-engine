.PHONY: setup backend frontend check format
setup:
	uv sync --frozen
	npm --prefix frontend ci
backend:
	uv run --frozen uvicorn infinite_engine.main:create_app --factory --reload --host 127.0.0.1
frontend:
	npm --prefix frontend run dev
check:
	uv run --frozen ruff format --check .
	uv run --frozen ruff check .
	uv run --frozen mypy
	uv run --frozen pytest
	uv run --frozen python scripts/check_docs.py
	npm --prefix frontend run format:check
	npm --prefix frontend run lint
	npm --prefix frontend run typecheck
	npm --prefix frontend test
	npm --prefix frontend run build
format:
	uv run --frozen ruff format .
	npm --prefix frontend run format
