#!/bin/bash

echo "Running Ruff (linter and formatter)..."
ruff check . --fix
ruff format .

echo "Running MyPy..."
mypy src

echo "Running Black..."
black .
