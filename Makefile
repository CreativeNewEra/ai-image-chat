# AI Image Chat - Development Makefile
# Common commands for development workflow

.PHONY: help format lint type-check test test-unit test-integration coverage clean all check install install-dev

# Default target - show help
help:
	@echo "AI Image Chat - Development Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  make format          - Format code with Black"
	@echo "  make lint            - Lint code with Ruff (auto-fix)"
	@echo "  make lint-check      - Lint code with Ruff (check only)"
	@echo "  make type-check      - Run mypy type checking"
	@echo "  make test            - Run all tests with pytest"
	@echo "  make test-unit       - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make coverage        - Generate test coverage report"
	@echo "  make check           - Run format + lint + type-check + test"
	@echo "  make all             - Same as 'make check'"
	@echo "  make clean           - Remove build artifacts and cache"
	@echo "  make install         - Install production dependencies"
	@echo "  make install-dev     - Install development dependencies"
	@echo ""

# Format code with Black
format:
	@echo "🎨 Formatting code with Black..."
	black core/ utils/ comfyui_api.py config.py app.py
	@echo "✅ Formatting complete!"

# Lint code with Ruff (auto-fix enabled)
lint:
	@echo "🔍 Linting code with Ruff..."
	ruff check . --fix
	@echo "✅ Linting complete!"

# Lint code with Ruff (check only, no auto-fix)
lint-check:
	@echo "🔍 Checking code with Ruff..."
	ruff check .

# Type check with mypy
type-check:
	@echo "🔍 Type checking with mypy..."
	mypy .
	@echo "✅ Type checking complete!"

# Run all tests
test:
	@echo "🧪 Running all tests..."
	pytest

# Run unit tests only
test-unit:
	@echo "🧪 Running unit tests..."
	pytest -m unit

# Run integration tests only
test-integration:
	@echo "🧪 Running integration tests..."
	pytest -m integration

# Generate coverage report
coverage:
	@echo "📊 Generating coverage report..."
	pytest --cov=core --cov=utils --cov-report=html --cov-report=term-missing
	@echo "✅ Coverage report generated in htmlcov/"

# Run all checks (format, lint, type-check, test)
check: format lint type-check test
	@echo "✅ All checks passed!"

# Alias for check
all: check

# Clean build artifacts and cache
clean:
	@echo "🧹 Cleaning build artifacts and cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml 2>/dev/null || true
	rm -rf build/ dist/ 2>/dev/null || true
	@echo "✅ Clean complete!"

# Install production dependencies
install:
	@echo "📦 Installing production dependencies..."
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements-dev.txt
	@echo "✅ Development environment ready!"
