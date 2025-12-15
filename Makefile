PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin

export PYTHONPATH := backend

.PHONY: install lint test check

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r backend/requirements-dev.txt

lint:
	$(BIN)/ruff backend/app backend/tests

test:
	@mkdir -p reports
	$(BIN)/pytest backend/tests --cov=backend/app --cov-report=term-missing --junitxml=reports/junit.xml

check: lint test
