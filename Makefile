PY ?= python3

all: check kit

check:
	cd src && $(PY) simbolo.py && $(PY) nombre.py && $(PY) splash.py && $(PY) horizontal.py

kit:
	cd src && $(PY) kit.py && $(PY) portada.py --probar

.PHONY: all check kit
