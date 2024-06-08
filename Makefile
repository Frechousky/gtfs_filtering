DIST_FOLDER=dist
TESTS_E2E_FOLDER=tests/e2e
TESTS_UNIT_FOLDER=tests/unit

# dependencies installation
install-deps:
	pipenv sync
install-all-deps:
	pipenv sync -d
update-deps:
	pipenv update

# linting & formatting
lint:
	pipenv run ruff check .
lint-fix:
	pipenv run ruff check . --fix
format:
	pipenv run ruff format --check .
format-fix:
	pipenv run ruff format .

# testing
e2e: package-cli
	pipenv run pytest "$(TESTS_E2E_FOLDER)"
unit:
	pipenv run pytest "$(TESTS_UNIT_FOLDER)"
tests: unit e2e

# packaging
$(DIST_FOLDER)/cli: gtfs_filtering/core.py gtfs_filtering/cli.py
	@echo "package cli application"
	pipenv run pyinstaller -F gtfs_filtering/cli.py 2>&1 > /dev/null
	rm -rf build/
	rm cli.spec
$(DIST_FOLDER)/gui: gtfs_filtering/core.py gtfs_filtering/gui.py
	@echo "package gui application"
	pipenv run pyinstaller -F gtfs_filtering/gui.py 2>&1 > /dev/null
	rm -rf build/
	rm gui.spec
package-cli: $(DIST_FOLDER)/cli
package-gui: $(DIST_FOLDER)/gui

clean:
	rm -rf dist/ .pytest_cache/ .ruff_cache

.PHONY: install-deps install-all-deps update-deps lint lint-fix format format-check e2e unit tests package-cli package-gui clean
