.PHONY: check lint format test

check: lint test

lint:
	ruff format --check .
	ruff check .

format:
	ruff format .
	ruff check --fix .

test:
	pytest
