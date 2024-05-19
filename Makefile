VENV_FOLDER=venv
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

test: $(VENV_FOLDER)
	pytest

.PHONY: clean
