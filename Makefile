-include .env
.PHONY: $(MAKECMDGOALS)

POETRY_VERSION := 2.1.3
HOST=0.0.0.0
PORT ?= 8000

# Help

help:
	@echo "          AVAILABLE COMMANDS"
	@echo "          venv  Creates Venv and .env"
	@echo "   install-dev  Installs all dependencies for Dev"
	@echo "  install-prod  Installs only Prod dependencies"
	@echo "         clean  Removes Venv, logs, and caches"
	@echo "       run-dev  Runs in Dev environment"
	@echo "      run-prod  Runs in Prod environment"
	@echo "        docker  Builds and runs in Docker Container"
	@echo "   docker-logs  Streams the Container's recent logs"
	@echo "          docs  Runs the documentation (MKDocs)"
	@echo "          test  Runs the tests (Pytest)"
	@echo "      coverage  Runs the test Coverage"
	@echo "        format  Runs the code formatters"
	@echo "          lint  Runs the code linters"
	@echo "    lint-tests  Runs the code linters on tests"
	@echo "       locales  Compiles the translation files"
	@echo "         audit  Runs vulnerability audits"
	@echo "           req  Compiles Prod requirements"
	@echo "       req-dev  Compiles Dev requirements"

# Environment

venv:
	@bash venv.sh
	@cp .env.example .env

install-dev:
	@pip install --no-cache-dir poetry==$(POETRY_VERSION)
	@poetry install --all-groups

install-prod:
	@pip install --no-deps -r requirements.txt

clean:
	@deactivate
	@rm -rf .venv/
	@rm -rf .logs/
	@rm -rf __pycache__/
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm .coverage


# Run

run-dev:
	@poetry run python3 -m src

run-prod:
	@gunicorn -c src/gunicorn.conf.py

docker:
	@docker build -q -t scopus-survey-api .
	@docker run -d --env HOST=${HOST} --env-file .env --name scopus-survey-api -p ${PORT}:${PORT} scopus-survey-api
	@docker ps --filter "name=scopus-survey-api"

docker-logs:
	@docker logs --tail 50 --follow scopus-survey-api


# Documentation

docs:
	@poetry run mkdocs serve


# Tests

test:
	@poetry run pytest --color=yes --log-format=%(asctime)s %(levelname)s %(message)s --log-date-format=%Y-%m-%d %H:%M:%S

coverage:
	@poetry run coverage erase
	@poetry run coverage run -m pytest -q
	@poetry run coverage report


# Formatting and Linting

format:
	@poetry run isort .
	@poetry run black .

lint:
	@poetry run isort src/ --check
	@poetry run black src/ --check
	@poetry run pylint src/
	@poetry run mypy src/
	@poetry run radon cc src/ -a -nc

lint-tests:
	@poetry run isort tests/ --check
	@poetry run black tests/ --check
	@poetry run pylint tests/
	@poetry run mypy tests/
	@poetry run radon cc tests/ -a -nc


# Compile Locales

locales:
	@msgfmt locales/en_US/LC_MESSAGES/web.po -o locales/en_US/LC_MESSAGES/web.mo
	@msgfmt locales/en_US/LC_MESSAGES/error.po -o locales/en_US/LC_MESSAGES/error.mo

	@msgfmt locales/pt_BR/LC_MESSAGES/web.po -o locales/pt_BR/LC_MESSAGES/web.mo
	@msgfmt locales/pt_BR/LC_MESSAGES/error.po -o locales/pt_BR/LC_MESSAGES/error.mo


# Vulnerability

audit:
	@poetry run pip-audit -l . || true
	@poetry run bandit -c pyproject.toml -r src/ || true
	@poetry run bandit -c pyproject.toml -r tests/ || true


# Requirements
# poetry self add poetry-plugin-export

req:
	@poetry export -f requirements.txt -o requirements.txt --without-hashes --without-urls --only main

req-dev:
	@poetry export -f requirements.txt -o requirements-dev.txt --without-hashes --without-urls --all-groups
