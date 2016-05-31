SHELL=/bin/bash

wheel: lint constants clean
	./setup.py bdist_wheel

constants: aegea/constants.json

aegea/constants.json:
	python -c "import aegea; aegea.initialize(); from aegea.util.constants import write; write()"

lint_deps:
	pip install flake8

lint: lint_deps
	./setup.py flake8
#	flake8 scripts/*

test: install
	coverage run --source=aegea ./test/test.py
	./setup.py test

init_docs:
	cd docs; sphinx-quickstart

docs:
	$(MAKE) -C docs html

install: clean
	python ./setup.py bdist_wheel
	pip install --upgrade dist/*.whl

clean:
	-rm -rf build dist
	-rm -rf *.egg-info

.PHONY: lint test docs install clean
