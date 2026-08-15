.PHONY: install test run serve

install:
	pip install -e ".[dev]"

test:
	pytest -q

run:
	bringup --scenario first-power health

serve:
	bringup serve
