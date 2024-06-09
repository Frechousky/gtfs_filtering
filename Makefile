# dependencies installation
install-deps:
	pipenv sync
install-all-deps:
	pipenv sync -d
update-deps:
	pipenv update
check-deps:
	pipenv check # check dependencies for vulnerabilities

# linting & formatting
lint-check:
	pipenv run ruff check .
lint:
	pipenv run ruff check . --fix
format-check:
	pipenv run ruff format --check .
format:
	pipenv run ruff format .

# testing
e2e: package-cli
	pipenv run pytest tests/e2e
unit:
	pipenv run pytest tests/unit
tests: unit e2e

# packaging
dist/cli: gtfs_filtering/core.py gtfs_filtering/cli.py
	@echo "package cli application"
	pipenv run pyinstaller -F gtfs_filtering/cli.py
	rm -rf build/ cli.spec
dist/gui: gtfs_filtering/core.py gtfs_filtering/gui.py
	@echo "package gui application"
	pipenv run pyinstaller -F gtfs_filtering/gui.py
	rm -rf build/ gui.spec
package-cli: dist/cli
package-gui: dist/gui

clean:
	rm -rf dist/ .pytest_cache/ .ruff_cache

.PHONY: install-deps install-all-deps update-deps lint-check lint format-check format e2e unit tests package-cli package-gui clean
