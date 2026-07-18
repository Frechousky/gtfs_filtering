# dependencies
install-deps:
	uv sync --no-dev
install-all-deps:
	uv sync --all-groups
update-deps:
	uv lock --upgrade
check-deps:
	uvx pip-audit

# linting & formatting
lint-check:
	uv run ruff check .
lint:
	uv run ruff check . --fix
format-check:
	uv run ruff format --check .
format:
	uv run ruff format .

# testing
e2e: cli
	uv run pytest tests/e2e
unit:
	uv run pytest tests/unit
tests: e2e unit

# packaging
dist/cli: gtfs_filtering/core.py gtfs_filtering/cli.py pyproject.toml uv.lock
	@echo "package cli application"
	uv run pyinstaller -F gtfs_filtering/cli.py
	rm -rf build/ cli.spec
dist/gui: gtfs_filtering/core.py gtfs_filtering/gui.py pyproject.toml uv.lock
	@echo "package gui application"
	uv run pyinstaller -F --add-data "assets:assets" gtfs_filtering/gui.py
	rm -rf build/ gui.spec
cli: dist/cli
gui: dist/gui

clean:
	rm -rf dist/ .pytest_cache/ .ruff_cache

.PHONY: install-deps install-all-deps update-deps check-deps lint-check lint format-check format e2e unit tests cli gui clean
