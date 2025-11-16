#!/bin/bash
# Bash script to clean up project cache and temporary files

echo "Cleaning up project..."

# Remove cache directories
echo "Removing cache directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null

# Remove compiled Python files
echo "Removing compiled Python files..."
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete

# Remove build artifacts
echo "Removing build artifacts..."
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
find . -type d -name "build" -exec rm -rf {} + 2>/dev/null
find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null

# Remove OS-specific files
echo "Removing OS-specific files..."
find . -type f -name ".DS_Store" -delete
find . -type f -name "Thumbs.db" -delete
find . -type d -name "__MACOSX" -exec rm -rf {} + 2>/dev/null

# Remove temporary files
echo "Removing temporary files..."
find . -type f -name "*.tmp" -delete
find . -type f -name "*.bak" -delete
find . -type f -name "*.backup" -delete

echo ""
echo "✅ Cleanup complete!"

