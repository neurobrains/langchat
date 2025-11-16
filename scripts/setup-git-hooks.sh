#!/bin/bash
# Bash script to set up git hooks for code quality checks

echo "Setting up git hooks..."

# Run Python setup script
python3 scripts/setup-git-hooks.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Git hooks setup complete!"
    echo ""
    echo "Hooks installed:"
    echo "  - pre-commit: Runs Ruff linting and formatting (auto-fixes issues)"
    echo "  - pre-push: Runs MyPy type checking on entire project"
    echo "  - prepare-commit-msg: Automatically adds DCO sign-off"
    echo ""
    echo "To test:"
    echo "  - Make a commit to trigger Ruff checks and auto sign-off"
    echo "  - Push to trigger MyPy checks"
else
    echo "❌ Failed to setup git hooks"
    exit 1
fi

