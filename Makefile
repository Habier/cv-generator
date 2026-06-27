PYTHON ?= python3
GEN := $(PYTHON) scripts/generate.py
TEMPLATE ?=

.PHONY: install test build-executable generate clean

install:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt -r requirements-dev.txt

test:
	$(PYTHON) -m pytest tests/

build-executable: test
	$(PYTHON) -m PyInstaller pyinstaller.spec --noconfirm --clean

generate:
	$(GEN) $(if $(TEMPLATE),--template $(TEMPLATE),)

clean:
	rm -rf output/*
