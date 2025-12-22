#!/bin/bash
# Script to run all code quality checks

echo "Running Ruff linting..."
python -m ruff check src/ tests/

echo ""
echo "Running ty type checking..."
python -m ty check src/

echo ""
echo "Running tests..."
python -m pytest tests/ -v

echo ""
echo "All checks completed!"

