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
	@echo "        secret  Generates a new secret key (URL-safe)"
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
	@echo "       measure  Measures code complexity and maintainability"
	@echo " measure-tests  Measures code complexity and maintainability on tests"
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

secret:
	@openssl rand -base64 64 | tr -d '\n=' | tr '/+' '_-'; echo ""

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
	@printf "\033[33mIsort:\033[m\n"
	@poetry run isort .
	@printf "\033[33mBlack:\033[m\n"
	@poetry run black .

lint:
	@printf "\033[33mIsort:\033[m\n"
	@poetry run isort src/ --check
	@printf "\033[33mBlack:\033[m\n"
	@poetry run black src/ --check
	@printf "\033[33mPylint:\033[m\n"
	@poetry run pylint src/
	@printf "\033[33mMypy:\033[m\n"
	@poetry run mypy src/

lint-tests:
	@printf "\033[33mIsort:\033[m\n"
	@poetry run isort tests/ --check
	@printf "\033[33mBlack:\033[m\n"
	@poetry run black tests/ --check
	@printf "\033[33mPylint:\033[m\n"
	@poetry run pylint tests/
	@printf "\033[33mMypy:\033[m\n"
	@poetry run mypy tests/


# Compile Locales

locales:
	@msgfmt locales/en_US/LC_MESSAGES/web.po -o locales/en_US/LC_MESSAGES/web.mo
	@msgfmt locales/en_US/LC_MESSAGES/error.po -o locales/en_US/LC_MESSAGES/error.mo

	@msgfmt locales/pt_BR/LC_MESSAGES/web.po -o locales/pt_BR/LC_MESSAGES/web.mo
	@msgfmt locales/pt_BR/LC_MESSAGES/error.po -o locales/pt_BR/LC_MESSAGES/error.mo


# Metrics

measure:
	@printf "\033[33mRadon [CC]:\033[m\n"
	@poetry run radon cc src/
	@printf "\033[33mRadon [MI]:\033[m\n"
	@poetry run radon mi src/

measure-tests:
	@printf "\033[33mRadon [CC]:\033[m\n"
	@poetry run radon cc tests/
	@printf "\033[33mRadon [MI]:\033[m\n"
	@poetry run radon mi tests/


# Vulnerability

audit:
	@printf "\033[33mPip-Audit:\033[m\n"
	@poetry run pip-audit -l . || true
	@printf "\033[33mBandit [src]:\033[m\n"
	@poetry run bandit -c pyproject.toml -r src/ || true
	@printf "\033[33mBandit [tests]:\033[m\n"
	@poetry run bandit -c pyproject.toml -r tests/ || true


# Requirements
# poetry self add poetry-plugin-export

req:
	@poetry export -f requirements.txt -o requirements.txt --without-hashes --without-urls --only main

req-dev:
	@poetry export -f requirements.txt -o requirements-dev.txt --without-hashes --without-urls --all-groups
