# Contributing to LangChat

Thank you for considering a contribution! Whether you're fixing a bug, adding a feature, or improving documentation — your help makes LangChat better for everyone.

---

## 1. Set Up Your Development Environment

LangChat uses [uv](https://docs.astral.sh/uv/) for fast, reproducible dependency management. Install it first if you don't have it:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then set up the project:

```bash
# 1. Fork & clone
git clone https://github.com/your-username/langchat.git
cd langchat

# 2. Create an isolated virtual environment
uv venv

# 3. Install the package + dev dependencies
uv pip install -e ".[dev]"

# 4. Activate (optional — uv run / uv pip work without it)
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

> **Why uv?** It is 10–100× faster than pip and resolves dependencies deterministically without a separate lock-file step.

---

## 2. Development Workflow

Always create a new branch:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### Run the tests

```bash
uv run pytest
# or, if your venv is active:
pytest
```

### Lint and format

```bash
# Check for issues
uv run ruff check .

# Auto-fix safe issues
uv run ruff check . --fix

# Format code
uv run ruff format .
```

Both checks must pass before opening a PR.

---

## 3. The Golden Rule: DCO Sign-off

All commits must include a sign-off to certify your contribution:

```bash
git commit -s -m "Brief description of your change"
```

This adds `Signed-off-by: Your Name <email>` to the commit message.

---

## 4. Project Architecture

| Module | Responsibility |
|--------|---------------|
| `src/langchat/providers/` | Clean, auto-env wrappers — the primary public API |
| `src/langchat/adapters/`  | Low-level service integrations (OpenAI, Pinecone, Supabase, …) |
| `src/langchat/core/`      | Chat engine, session management, prompt logic |
| `src/langchat/api/`       | FastAPI app, routes, and request/response models |
| `src/langchat/types.py`   | Public typed return values (`ChatResponse`) |
| `tests/`                  | Mirrors the `src/` structure; uses `pytest` + `pytest-asyncio` |
| `examples/`               | Real-life usage examples — keep these up to date with API changes |

---

## 5. Adding a New LLM Provider

1. Create `src/langchat/adapters/llm/yourprovider_provider.py` following the pattern of existing providers (see `anthropic_provider.py`).
2. Export it from `src/langchat/adapters/llm/__init__.py`.
3. Add an auto-env wrapper in `src/langchat/providers/__init__.py`.
4. Add tests in `tests/providers/test_providers.py`.
5. Add the provider to the README provider table.

---

## 6. Pull Request Checklist

Before opening a PR, confirm:

- [ ] All tests pass: `uv run pytest`
- [ ] Lint is clean: `uv run ruff check .`
- [ ] Code is formatted: `uv run ruff format --check .`
- [ ] Type hints added for any new public functions
- [ ] Relevant tests added or updated
- [ ] Every commit is signed off with `-s`
- [ ] Documentation (README / docstrings) updated if needed

---

## 7. Found a Bug or Have an Idea?

- **Bug**: Open an issue with a clear description and steps to reproduce.
- **Feature**: Start a discussion in [Issues](https://github.com/neurobrains/langchat/issues).

---

<p align="center">
  <a href="https://github.com/neurobrains/langchat/issues">Open an Issue</a> •
  <a href="https://langchat.neurobrains.co/">Documentation</a>
</p>
