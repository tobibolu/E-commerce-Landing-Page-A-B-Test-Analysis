PYTHON ?= python

install:
	$(PYTHON) -m pip install -e '.[dev]'

lint:
	ruff check src tests scripts
	black --check src tests scripts
	mypy src

test:
	pytest -q

run-analysis:
	$(PYTHON) scripts/run_analysis.py
