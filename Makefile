PYTHON ?= python3
GEN := $(PYTHON) scripts/generate.py
TEMPLATE ?= classic

.PHONY: install html pdf all all-templates clean backend-es backend-en fullstack-es fullstack-en backend-es-laravel backend-en-laravel fullstack-es-laravel fullstack-en-laravel preview-templates

install:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

html:
	$(GEN) --profile backend --lang es --template $(TEMPLATE)
	$(GEN) --profile backend --lang en --template $(TEMPLATE)
	$(GEN) --profile fullstack --lang es --template $(TEMPLATE)
	$(GEN) --profile fullstack --lang en --template $(TEMPLATE)

pdf:
	$(GEN) --profile backend --lang es --template $(TEMPLATE) --pdf
	$(GEN) --profile backend --lang en --template $(TEMPLATE) --pdf
	$(GEN) --profile fullstack --lang es --template $(TEMPLATE) --pdf
	$(GEN) --profile fullstack --lang en --template $(TEMPLATE) --pdf

all: pdf

all-templates:
	$(MAKE) pdf TEMPLATE=classic
	$(MAKE) pdf TEMPLATE=pdf-like
	$(MAKE) pdf TEMPLATE=compact
	$(MAKE) pdf TEMPLATE=sidebar
	$(MAKE) pdf TEMPLATE=ats-clean

preview-templates:
	$(GEN) --profile backend --lang es --template classic
	$(GEN) --profile backend --lang es --template pdf-like
	$(GEN) --profile backend --lang es --template compact
	$(GEN) --profile backend --lang es --template sidebar
	$(GEN) --profile backend --lang es --template ats-clean

backend-es:
	$(GEN) --profile backend --lang es --template $(TEMPLATE) --pdf

backend-en:
	$(GEN) --profile backend --lang en --template $(TEMPLATE) --pdf

fullstack-es:
	$(GEN) --profile fullstack --lang es --template $(TEMPLATE) --pdf

fullstack-en:
	$(GEN) --profile fullstack --lang en --template $(TEMPLATE) --pdf

backend-es-laravel:
	$(GEN) --profile backend --lang es --focus laravel --template $(TEMPLATE) --pdf

backend-en-laravel:
	$(GEN) --profile backend --lang en --focus laravel --template $(TEMPLATE) --pdf

fullstack-es-laravel:
	$(GEN) --profile fullstack --lang es --focus laravel --template $(TEMPLATE) --pdf

fullstack-en-laravel:
	$(GEN) --profile fullstack --lang en --focus laravel --template $(TEMPLATE) --pdf

clean:
	rm -rf output/*
