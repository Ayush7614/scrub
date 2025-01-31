.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python3 -c "$$BROWSER_PYSCRIPT"

help:
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

all: lint test docs  ## Equivalent to running make on the lint, test, and docs targets

clean: clean-build clean-pyc clean-test clean-docs ## remove all build, test, coverage, docs and Python artifacts
	rm -fr reports

clean-build:  ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-docs:  ## remove generated documentation products from ./docs
	rm -f docs/scrub.rst
	rm -f docs/modules.rst
	rm -f docs/scrub.targets.*
	rm -f docs/scrub.utils.*
	rm -f docs/scrub.tools.*
	$(MAKE) -C docs clean

clean-pyc: ## remove Python file artifacts (bute code, etc.)
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr .pytest_cache
	rm -fr reports

lint: ## check style of ./scrub with pylint
	mkdir -p reports/pylint
	-pylint -d W0511 scrub | tee reports/pylint/pylint_report.txt
	$(BROWSER) reports/pylint/pylint_report.txt

test: install-dev  ## runs test suite in ./tests
	pytest -v --cov=scrub \
	--html=reports/pytest/index.html tests/
	$(BROWSER) reports/pytest/index.html
	coverage3 html -d reports/coverage/
	$(BROWSER) reports/coverage/index.html

coverage: ## check coverage of ./tests on ./scrub
	coverage3 run --source scrub -m pytest -v --junit-xml=./reports/regression_results.xml
	coverage3 report -m >> ./reports/coverage_results.txt
	coverage3 html -d reports/coverage/
	$(BROWSER) reports/coverage/index.html

docs: clean-docs ## make Sphinx HTML docs for scrub (including API)
	mkdir -p docs/_static
	mkdir -p docs/_build
	sphinx-apidoc -o docs/ scrub
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html
	rm -f docs/scrub.*
	rm -f docs/modules.rst

# servedocs: docs ## compile the docs watching for changes
# 	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

# release: dist ## package and upload a release
# 	twine upload dist/*

dist: clean ## builds python source and wheel package using setuptools
	python3 setup.py sdist
	python3 setup.py bdist_wheel
	ls -l dist

install: clean-build ## install scrub to site-packages
	python3 -m pip install .

install-dev: clean-build ## install scrub to site-packages for development
	python3 -m pip install -e .

uninstall:  ## remove the installed scrub package
	python3 -m pip uninstall -y scrub
