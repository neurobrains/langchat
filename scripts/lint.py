# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

import sys
from functools import partial

try:
    from utils import Package, die, for_each_package  # type: ignore[import-untyped]
except ImportError:
    # Fallback: Define minimal stubs if utils module is not available
    print("Warning: utils module not found. Lint script may not work correctly.", file=sys.stderr)
    
    class Package:
        def __init__(self, name: str, path: str):
            self.name = name
            self.path = path
        
        def run_cmd(self, cmd: str):
            return (0, "")
    
    def die(msg: str):
        print(msg, file=sys.stderr)
        sys.exit(1)
    
    def for_each_package(func):
        # No-op if no packages are defined
        pass


def run_cmd_or_die(
    cmd: str,
    description: str,
    package: Package,
) -> None:
    print(f"Running {cmd} on {package.name}...")

    status, output = package.run_cmd(cmd)

    if status != 0:
        print(output, file=sys.stderr)
        die(f"error: package '{package.path}': {description}")


def lint_package(ty: bool, ruff: bool, package: Package) -> None:
    if ty:
        run_cmd_or_die("ty check", "Please fix ty lint errors", package)
    if ruff:
        run_cmd_or_die("ruff check", "Please fix Ruff lint errors", package)
        run_cmd_or_die("ruff format --check", "Please format files with Ruff", package)


if __name__ == "__main__":
    ty = "--ty" in sys.argv
    ruff = "--ruff" in sys.argv

    for_each_package(partial(lint_package, ty, ruff))
