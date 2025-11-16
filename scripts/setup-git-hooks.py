#!/usr/bin/env python3
"""
Setup git hooks for code quality checks.
Copies hooks from scripts/hooks/ to .git/hooks/
Works on Windows, Linux, and Mac.
"""

import os
import platform
import shutil
import stat
import sys
from pathlib import Path


def make_executable(filepath):
    """Make a file executable."""
    try:
        current_permissions = os.stat(filepath).st_mode
        os.chmod(filepath, current_permissions | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    except Exception:
        pass  # On Windows, this might not work, but that's okay


def create_universal_wrapper(hook_name, hooks_target_dir, hooks_source_dir, python_exe):
    """Create a universal shell script wrapper for Python hooks that works on Windows (Git Bash) and Unix."""
    hook_file = hooks_target_dir / hook_name
    # Use absolute path to source script (resolve to handle any symlinks/relative paths)
    source_script = hooks_source_dir.resolve() / hook_name
    # Convert Windows paths to Unix-style for Git Bash compatibility
    if platform.system() == "Windows":
        # Convert Windows path to Git Bash compatible path
        source_script_str = str(source_script).replace("\\", "/")
        # Handle drive letters (E:/path -> /e/path for Git Bash)
        if len(source_script_str) > 1 and source_script_str[1] == ":":
            drive_letter = source_script_str[0].lower()
            source_script_str = f"/{drive_letter}{source_script_str[2:]}"
        python_exe_str = str(python_exe).replace("\\", "/")
        if len(python_exe_str) > 1 and python_exe_str[1] == ":":
            drive_letter = python_exe_str[0].lower()
            python_exe_str = f"/{drive_letter}{python_exe_str[2:]}"
    else:
        source_script_str = str(source_script)
        python_exe_str = python_exe

    # Create shell script that works with Git Bash and Unix shells
    shell_content = f'''#!/bin/sh
# {hook_name} hook wrapper
# This calls the Python script from scripts/hooks/
# Works on Windows (Git Bash), Linux, and Mac

# Try to find Python executable
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    # Fallback to absolute path (for Windows Git Bash)
    PYTHON_CMD="{python_exe_str}"
fi

# Execute the hook script
exec "$PYTHON_CMD" "{source_script_str}" "$@"
'''
    with open(hook_file, "w", encoding="utf-8", newline="\n") as f:
        f.write(shell_content)
    make_executable(hook_file)
    return hook_file


def setup_hooks():
    """Set up git hooks by copying from scripts/hooks/ to .git/hooks/."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    hooks_source_dir = script_dir / "hooks"
    hooks_target_dir = repo_root / ".git" / "hooks"

    if not hooks_source_dir.exists():
        print(f"❌ Hooks source directory not found: {hooks_source_dir}")
        return False

    if not hooks_target_dir.exists():
        hooks_target_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created hooks directory: {hooks_target_dir}")

    # Get Python executable
    python_exe = sys.executable

    # Detect Windows
    platform.system() == "Windows"

    # List of hooks to copy
    hook_files = ["pre-commit", "pre-push", "prepare-commit-msg"]

    success = True
    for hook_name in hook_files:
        source_file = hooks_source_dir / hook_name
        target_file = hooks_target_dir / hook_name

        if not source_file.exists():
            print(f"⚠ {hook_name} source file not found: {source_file}")
            continue

        try:
            # For Python hooks, create a universal shell script wrapper
            if hook_name in ["pre-commit", "pre-push"]:
                # Create shell script wrapper that calls script from scripts/hooks/
                create_universal_wrapper(hook_name, hooks_target_dir, hooks_source_dir, python_exe)
                print(f"✓ Installed {hook_name} hook (shell wrapper → scripts/hooks/{hook_name})")
            else:
                # For bash scripts, copy directly
                shutil.copy2(source_file, target_file)
                make_executable(target_file)
                print(f"✓ Installed {hook_name} hook")
        except Exception as e:
            print(f"❌ Failed to install {hook_name}: {e}")
            success = False

    return success


if __name__ == "__main__":
    print("Setting up git hooks...")
    print("=" * 60)

    if setup_hooks():
        print("=" * 60)
        print("\n✅ Git hooks setup complete!")
        print("\nHooks installed:")
        print("  - pre-commit: Runs Ruff linting and formatting (auto-fixes issues)")
        print("  - pre-push: Runs MyPy type checking on entire project")
        print("  - prepare-commit-msg: Automatically adds DCO sign-off (bash script)")
        print("\nHooks source: scripts/hooks/")
        print("Hooks target: .git/hooks/")
        print(
            "\nNote: Shell script wrappers are created that work on Windows (Git Bash), Linux, and Mac"
        )
    else:
        print("\n❌ Failed to setup some hooks")
        sys.exit(1)
