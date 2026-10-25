.PHONY: setup run test test-cov lint lint-fix format check clean help

help:
	@echo "Available commands:"
	@echo "  make setup     - Install dependencies using uv"
	@echo "  make run       - Run the FastAPI application"
	@echo "  make test      - Run test suite"
	@echo "  make test-cov  - Run tests with coverage"
	@echo "  make lint      - Lint code with ruff"
	@echo "  make format    - Format code with ruff"
	@echo "  make check     - Check format and lint"
	@echo "  make clean     - Remove cache files"

setup:
	@echo "Setting up virtual environment and dependencies..."
	uv sync

run:
	@echo "Starting Theodore Telephony Core..."
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

test:
	@echo "Running tests..."
	uv run pytest -v

test-cov:
	@echo "Running tests with coverage..."
	uv run pytest --cov=src --cov-report=term-missing test/

lint:
	@echo "Checking linting..."
	uv run ruff check src test

lint-fix:
	@echo "Fixing lint issues..."
	uv run ruff check --fix src test

format:
	@echo "Formatting code..."
	uv run ruff format src test

check: lint format

clean:
	@echo "Cleaning up caches..."
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
