#!/bin/bash

# Setup script to install the DCO sign-off git hook
# This script copies the prepare-commit-msg hook to your .git/hooks directory

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOK_SOURCE="$REPO_ROOT/scripts/prepare-commit-msg"
HOOK_DEST="$REPO_ROOT/.git/hooks/prepare-commit-msg"

if [ ! -f "$HOOK_SOURCE" ]; then
  echo "Error: prepare-commit-msg hook not found at $HOOK_SOURCE"
  exit 1
fi

# Copy the hook
cp "$HOOK_SOURCE" "$HOOK_DEST"

# Make it executable
chmod +x "$HOOK_DEST"

echo "✅ DCO sign-off hook installed successfully!"
echo "The hook will automatically append DCO sign-off to your commit messages."

