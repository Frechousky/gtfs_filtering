# dependencies
install-deps:
	uv sync --no-dev
install-cli-deps:
	uv sync --no-dev --extra cli
install-gui-deps:
	uv sync --no-dev --extra gui
install-web-deps:
	uv sync --no-dev --extra web
install-all-deps:
	uv sync --all-groups --all-extras
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
	uv run --extra web pytest tests/unit
tests: e2e unit

# packaging
dist/cli: gtfs_filtering/core.py gtfs_filtering/cli.py pyproject.toml uv.lock
	@echo "package cli application"
	uv run --extra cli pyinstaller -F gtfs_filtering/cli.py
	rm -rf build/ cli.spec
dist/gui: gtfs_filtering/core.py gtfs_filtering/gui.py pyproject.toml uv.lock
	@echo "package gui application"
	uv run --extra gui pyinstaller -F --add-data "assets:assets" gtfs_filtering/gui.py
	rm -rf build/ gui.spec
cli: dist/cli
gui: dist/gui

# web api
web:
	uv run --extra web uvicorn gtfs_filtering.web.main:app --host 0.0.0.0 --port 8000

clean:
	rm -rf dist/ .pytest_cache/ .ruff_cache

.PHONY: install-deps install-cli-deps install-gui-deps install-web-deps install-all-deps update-deps check-deps lint-check lint format-check format e2e unit tests cli gui web clean
