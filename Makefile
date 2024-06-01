VENV_FOLDER=venv
TESTS_E2E_FOLDER=tests/e2e
TESTS_UNIT_FOLDER=tests/unit
TOUCH_FILE=$(VENV_FOLDER)/touch
PIP=pip3
PYTHON=python3
REQ_TXT=requirements.txt

# creates venv folder
$(VENV_FOLDER): $(TOUCH_FILE)

# update venv deps if requirements.txt file is updated
$(TOUCH_FILE): $(REQ_TXT)
	test -d venv || virtualenv "$(VENV_FOLDER)"
	source "$(VENV_FOLDER)/bin/activate" \
	&& "$(PIP)" install --upgrade pip \
	&& "$(PIP)" install -r "$(REQ_TXT)" \
	&& touch "$(TOUCH_FILE)"

# deletes venv folder and *.pyc files
clean:
	rm -rf $(VENV_FOLDER)
	find -iname "*.pyc" -delete

# end to end testing
e2e: $(VENV_FOLDER)
	pytest "$(TESTS_E2E_FOLDER)"

# unit testing
unit: $(VENV_FOLDER)
	pytest "$(TESTS_UNIT_FOLDER)"

# all tests
tests: $(VENV_FOLDER)
	pytest

.PHONY: clean e2e unit tests
