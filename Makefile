VENV_FOLDER=venv
DIST_FOLDER=dist
TESTS_E2E_FOLDER=tests/e2e
TESTS_UNIT_FOLDER=tests/unit
TOUCH_FILE=$(VENV_FOLDER)/touch
PIP=pip3
PYTHON=python3
REQS_TXT=requirements-core.txt requirements-cli.txt requirements-gui.txt requirements-packaging.txt requirements-tests.txt

# creates venv folder
$(VENV_FOLDER): $(TOUCH_FILE)

# update venv deps if requirements-*.txt file are updated
$(TOUCH_FILE): $(REQS_TXT)
	test -d venv || virtualenv "$(VENV_FOLDER)"
	source "$(VENV_FOLDER)/bin/activate" \
	&& "$(PIP)" install --upgrade pip \
	&& for f in $(REQS_TXT); do "$(PIP)" install -r "$$f"; done \
	&& touch "$(TOUCH_FILE)"

# deletes venv folder and *.pyc files
clean:
	rm -rf $(VENV_FOLDER) $(DIST_FOLDER)
	find -iname "*.pyc" -delete

# end to end testing
e2e: $(VENV_FOLDER) package-cli
	pytest "$(TESTS_E2E_FOLDER)"

# unit testing
unit: $(VENV_FOLDER)
	pytest "$(TESTS_UNIT_FOLDER)"

# all tests
tests: unit e2e

# build CLI executable
$(DIST_FOLDER)/cli: $(VENV_FOLDER)
	pyinstaller -F gtfs_filtering/cli.py
	rm -rf build/
	rm cli.spec

package-cli: $(DIST_FOLDER)/cli

# build GUI executable
$(DIST_FOLDER)/gui: $(VENV_FOLDER)
	pyinstaller -F gtfs_filtering/gui.py
	rm -rf build/
	rm gui.spec

package-gui: $(DIST_FOLDER)/gui

.PHONY: clean e2e unit tests package-cli package-gui
