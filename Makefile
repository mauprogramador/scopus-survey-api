.PHONY: $(MAKECMDGOALS)


# Environment

setup:
	@bash setup.sh

install:
	@poetry install --no-root


# Run application

run:
	@poetry run python3 -m app.framework.fastapi.main


# Documentation

docs:
	@poetry run mkdocs serve


# Tests

test:
	@poetry run pytest -v --color=yes

test-docker:
	@docker exec -it scopus-api pytest -v --color=yes

coverage:
	@poetry run coverage erase
	@poetry run coverage run -m pytest -q
	@poetry run coverage report

coverage-docker:
	@docker exec -it scopus-api coverage erase && coverage run -m pytest -q && coverage report


# Vulnerability audit

audit:
	@poetry run pip-audit
	@poetry run bandit -r app/ -c "pyproject.toml"
	@poetry run bandit -r tests/ -c "pyproject.toml"


# Formatting and Linting

format:
	@poetry run isort .
	@poetry run black .

lint:
	@poetry run isort app/ --check
	@poetry run black app/ --check
	@poetry run pylint app/
	@poetry run mypy app/
	@poetry run radon cc app/ -a -nc

lint-tests:
	@poetry run isort tests/ --check
	@poetry run black tests/ --check
	@poetry run pylint tests/
	@poetry run mypy tests/
	@poetry run radon cc tests/ -a -nc


# Docker: build image and run container

docker:
	@docker build -q -t scopus-searcher-api -f docker/Dockerfile .
	@docker run -d -p 8000:8000 --name scopus-api scopus-searcher-api

docker-docs:
	@docker build -q -t scopus-searcher-docs -f docker/Dockerfile.docs .
	@docker run -d -p 8001:8000 --name scopus-docs scopus-searcher-docs


# Requirements

req:
	@poetry export -f requirements.txt -o requirements/requirements.txt --without-hashes --without-urls --only main

req-dev:
	@poetry export -f requirements.txt -o requirements/dev_requirements.txt --without-hashes --without-urls --with dev

req-docs:
	@poetry export -f requirements.txt -o requirements/docs_requirements.txt --without-hashes --without-urls --with docs

req-test:
	@poetry export -f requirements.txt -o requirements/tests_requirements.txt --without-hashes --without-urls --with test

req-all:
	@poetry export -f requirements.txt -o requirements/all_requirements.txt --without-hashes --without-urls --with dev --with docs --with test
