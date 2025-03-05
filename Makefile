.PHONY: help venv install install-dev clean test lint format check run-web run-cli docs env-setup

# Python and virtualenv settings
PYTHON := python3
VENV := .venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip

# Web application settings
FLASK_HOST ?= 0.0.0.0
FLASK_PORT ?= 5000
FLASK_DEBUG ?= 1

# Colors for help messages
BLUE=\033[0;34m
GREEN=\033[0;32m
RED=\033[0;31m
NC=\033[0m # No Color
BOLD=\033[1m

help: ## Show this help message
	@echo '${BLUE}Usage:${NC}'
	@echo '  make ${GREEN}<target>${NC}'
	@echo ''
	@echo '${BLUE}Targets:${NC}'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${GREEN}%-20s${NC} %s\n", $$1, $$2}'

# Virtual environment
venv: ## Create virtual environment if it doesn't exist
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV); \
	fi

activate-venv: venv ## Activate virtual environment (in current shell)
	@echo "To activate the virtual environment, run:"
	@echo "source $(VENV)/bin/activate"

# Installation targets
install: venv ## Install package and dependencies
	$(VENV_PIP) install -e .

install-dev: venv ## Install development dependencies
	$(VENV_PIP) install -e ".[dev]"

# Cleaning targets
clean: ## Clean up Python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +

clean-venv: ## Remove virtual environment
	rm -rf $(VENV)

clean-all: clean clean-venv ## Clean everything including virtual environment

# Testing and quality targets
test: venv ## Run tests
	$(VENV_BIN)/pytest

test-cov: venv ## Run tests with coverage
	$(VENV_BIN)/pytest --cov=finanalyzer --cov-report=term-missing

lint: venv ## Run linting (flake8)
	$(VENV_BIN)/flake8 finanalyzer tests

typecheck: venv ## Run type checking (mypy)
	$(VENV_BIN)/mypy finanalyzer

format: venv ## Format code (black)
	$(VENV_BIN)/black finanalyzer tests
	$(VENV_BIN)/isort finanalyzer tests

check: lint typecheck format ## Run all code quality checks

# Application running targets
run-web: venv ## Run the web application
	FLASK_DEBUG=$(FLASK_DEBUG) \
	FLASK_APP=finanalyzer.web.app \
	$(VENV_PYTHON) scripts/run_webapp.py

run-web-flask: venv ## Run the web application using Flask CLI
	FLASK_DEBUG=$(FLASK_DEBUG) \
	FLASK_APP=finanalyzer.web.app \
	$(VENV_BIN)/flask run --host=$(FLASK_HOST) --port=$(FLASK_PORT)

run-cli: venv ## Run the CLI (requires additional arguments)
	@if [ "$(args)" = "" ]; then \
		echo "${RED}Error: CLI arguments required${NC}"; \
		echo "Usage: ${GREEN}make run-cli args=\"process /path/to/data -u John\"${NC}"; \
		exit 1; \
	fi
	$(VENV_PYTHON) scripts/run_cli.py $(args)

# Documentation targets
docs: venv ## Generate documentation
	cd docs && $(VENV_BIN)/make html

# Environment setup targets
env-setup: ## Create .env file from template if it doesn't exist
	@if [ ! -f ".env" ]; then \
		if [ -f ".env.example" ]; then \
			cp .env.example .env; \
			echo "${GREEN}Created .env file from template${NC}"; \
			echo "Edit .env file to customize your settings"; \
		else \
			echo "${RED}Error: .env.example file not found${NC}"; \
			exit 1; \
		fi \
	else \
		echo "${BLUE}Note: .env file already exists${NC}"; \
	fi

dev-setup: clean-all venv install-dev env-setup ## Setup development environment from scratch

# Environment information
env-info: ## Display information about the Python environment
	@echo "Python: $$($(PYTHON) --version)"
	@if [ -d "$(VENV)" ]; then \
		echo "Virtual environment: $(VENV) (exists)"; \
		echo "Packages:"; \
		$(VENV_PIP) list; \
	else \
		echo "Virtual environment: $(VENV) (not created)"; \
	fi
