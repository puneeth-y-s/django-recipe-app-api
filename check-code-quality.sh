#!/bin/bash

black --config .black.toml  .
pylint --rcfile .pylintrc *.py ./recipe/*.py ./user/*.py
flake8 --config .flake8 .
mypy --exclude venv .
ruff --config ruff.toml . --fix
isort --settings .isort.cfg .