#!/bin/bash
# Script to run all code quality checks

echo "Running Ruff linting..."
python -m ruff check src/ tests/

echo ""
echo "Running Ruff formatting check..."
python -m ruff format --check src/ tests/

echo ""
echo "Running MyPy type checking..."
python -m mypy src/ --config-file mypy.ini

echo ""
echo "Running tests..."
python -m pytest tests/ -v

echo ""
echo "All checks completed!"

