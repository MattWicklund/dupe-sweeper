.PHONY: test lint fix check install-dev

install-dev:
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest

lint:
	python3 -m ruff check .

fix:
	python3 -m ruff check . --fix

check:
	python3 -m ruff check .
	python3 -m pytest
