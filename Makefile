.PHONY: format
format:
	poetry run pysen run format

.PHONY: lint
lint:
	poetry run pysen run lint

.PHONY: test
test:
	poetry run pytest tests/*

.PHONY: install
install:
	poetry install

.PHONY: run
run:
	poetry run python main.py
