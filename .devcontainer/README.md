# Dev Container Setup

This project includes a VS Code Dev Container configuration for a consistent development environment.

## Features

- ✅ Python 3.11
- ✅ Pre-configured VS Code extensions
- ✅ Auto-install dependencies on container creation
- ✅ Git hooks automatically set up
- ✅ Ruff and MyPy pre-configured

## Usage

### Prerequisites
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Install [VS Code](https://code.visualstudio.com/)
3. Install [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Opening in Container

1. Open project in VS Code
2. Press `F1` or `Ctrl+Shift+P`
3. Select "Dev Containers: Reopen in Container"
4. Wait for container to build (first time takes a few minutes)
5. Dependencies will be installed automatically

### What Happens on Container Creation

- Python 3.11 is installed
- Project dependencies are installed via pip
- Git hooks are set up automatically
- VS Code extensions are installed
- Python path is configured

## Manual Setup (if needed)

If automatic setup fails:

```bash
# Install dependencies
pip install -e ".[dev]"

# Setup git hooks
python scripts/setup-git-hooks.py
```

## Troubleshooting

### Container Won't Start
- Ensure Docker Desktop is running
- Check Docker has enough resources (4GB RAM recommended)
- Try rebuilding: `F1` → "Dev Containers: Rebuild Container"

### Dependencies Not Installing
- Check internet connection
- Try manual install: `pip install -e ".[dev]"`
- Check Python version: `python --version`

### Git Hooks Not Working
- Run: `python scripts/setup-git-hooks.py`
- Check hooks exist: `ls -la .git/hooks/`

## Customization

Edit `.devcontainer/devcontainer.json` to:
- Change Python version
- Add more VS Code extensions
- Install additional system packages
- Configure environment variables

