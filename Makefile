PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
VENV ?= .venv

.PHONY: setup install dev lint format typecheck test test-one build run

setup:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate; $(PIP) install -U pip
	. $(VENV)/bin/activate; $(PIP) install -e .[dev]

install:
	$(PIP) install -e .

dev:
	$(PIP) install -e .[dev]

lint:
	ruff check src tests

format:
	black src tests

typecheck:
	mypy src

test:
	pytest

test-one:
	pytest -k "$(k)" -q

build:
	$(PYTHON) -m build

run:
	forge --help
