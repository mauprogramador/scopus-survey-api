-include .env
.PHONY: $(MAKECMDGOALS)

PORT ?= 8000


# Environment setup

venv:
	@bash venv.sh

install:
	@poetry install --no-root


# Run application

run:
	@poetry run python3 -m src

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
	@poetry run pytest -v --color=yes

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
	@msgfmt web/locales/en_US/LC_MESSAGES/web.po -o web/locales/en_US/LC_MESSAGES/web.mo
	@msgfmt web/locales/en_US/LC_MESSAGES/error.po -o web/locales/en_US/LC_MESSAGES/error.mo

	@msgfmt web/locales/pt_BR/LC_MESSAGES/web.po -o web/locales/pt_BR/LC_MESSAGES/web.mo
	@msgfmt web/locales/pt_BR/LC_MESSAGES/error.po -o web/locales/pt_BR/LC_MESSAGES/error.mo


# Vulnerability audit

audit:
	@poetry run pip-audit
	@poetry run bandit -r src/ -c "pyproject.toml"
	@poetry run bandit -r tests/ -c "pyproject.toml"


# Requirements
# poetry self add poetry-plugin-export

req:
	@poetry export -f requirements.txt -o requirements.txt --without-hashes --without-urls --only main

req-dev:
	@poetry export -f requirements.txt -o requirements-dev.txt --without-hashes --without-urls --all-groups
