PYTHON ?= python3
GEN := $(PYTHON) scripts/generate.py
TEMPLATE ?=

.PHONY: install pdf all all-templates clean

install:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

pdf:
	$(GEN) $(if $(TEMPLATE),--template $(TEMPLATE),)

all: pdf

all-templates:
	@for template in templates/*; do \
		if [ -f "$$template/cv.html.j2" ]; then \
			$(GEN) --template "$$(basename "$$template")"; \
		fi; \
	done

clean:
	rm -rf output/*
