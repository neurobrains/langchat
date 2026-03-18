# LangChat - Production-Grade AI Chatbot Framework

## Project Overview
LangChat is a Python library for building enterprise-scale AI chatbots with built-in conversational management, designed for production use where SLAs, stability, and security are critical.

- **Repository:** https://github.com/neurobrains/langchat
- **PyPI package:** `langchat`
- **Python:** ≥ 3.9
- **Package manager:** `uv` (`uv pip install -e ".[dev]"`)

---

## Architecture

**Hexagonal Architecture (Ports and Adapters)**

```
src/langchat/
├── core/                   # Domain logic — NEVER import adapters here
│   ├── engine.py           # LangChatEngine — orchestration core
│   ├── session.py          # UserSession — per-user state
│   ├── interfaces/         # Abstract base classes (ports)
│   └── utils/              # Pure helpers (document_indexer, etc.)
├── adapters/               # 3rd-party integrations (implement core interfaces)
│   ├── llm/                # OpenAI, Anthropic, Gemini, Mistral, Cohere, Ollama
│   ├── vector_db/          # Pinecone
│   ├── database/           # Supabase
│   ├── reranker/           # Flashrank
│   └── logger.py           # Shared logger
├── providers/              # Clean public API wrappers (auto-read env vars)
│   └── __init__.py         # OpenAI, Anthropic, Gemini, Mistral, Cohere, Ollama,
│                           #   Pinecone, Supabase
├── api/                    # FastAPI REST layer (consumes core only)
│   ├── routes.py
│   └── models.py
├── sdk.py                  # LangChat — main user-facing class
├── types.py                # ChatResponse dataclass
└── __init__.py             # Public re-exports + __version__

tests/                      # Mirrors src/langchat/
```

### Boundary Rules
- `core/` must never import from `adapters/` or `providers/`
- `adapters/` implement interfaces defined in `core/interfaces/`
- `providers/` wrap `adapters/` with auto-env-var loading
- `api/` imports only from `core/` and `sdk.py`
- `sdk.py` is the single public entry point for library users

---

## Tech Stack

| Area | Tool |
|------|------|
| Language | Python 3.9+ |
| Type checking | `ty` (strict) |
| Linting / formatting | `ruff` |
| Testing | `pytest` + `pytest-asyncio` (`asyncio_mode = "auto"`) |
| API framework | FastAPI |
| Package manager | uv |
| Frontend (demo UI) | React + Vite + TypeScript |

---

## Quality Gate — Run Before Every Commit

Run these **in order**. All five must pass with zero errors.

```bash
# 1. Auto-format (may rewrite files — do this first)
ruff format .

# 2. Lint and auto-fix safe issues
ruff check . --fix

# 3. Verify lint is clean (no remaining issues)
ruff check .

# 4. Strict type check (unset VIRTUAL_ENV on Windows to avoid venv conflicts)
unset VIRTUAL_ENV && ty check .

# 5. Full test suite
python -m pytest
```

Quick one-liner:
```bash
ruff format . && ruff check . --fix && ruff check . && unset VIRTUAL_ENV && ty check . && python -m pytest
```

> **If any step fails, fix it before proceeding.** Never commit with failing checks.

---

## DCO Sign-Off — Required on Every Commit

This project requires a **Developer Certificate of Origin** sign-off on every commit.

```bash
# Always use -s (--signoff)
git commit -s -m "feat: add streaming support to OpenAI adapter"
```

This appends `Signed-off-by: Your Name <your@email.com>` to the commit message.

See `DCO.md` for the full certificate text. PRs without signed commits will fail CI.

---

## Python 3.9 Compatibility — `from __future__ import annotations`

`requires-python = ">=3.9"` means `X | Y` union syntax (PEP 604) is only valid at
runtime on Python 3.10+. To use it in **all** Python files:

```python
from __future__ import annotations  # MUST be first import in every file
```

**Rules:**
- Add this line as the **first non-comment import** in every new Python file
- Files using `str | None`, `list[str] | None`, `X | Y` **must** have it
- Without it, `ty` will raise `unsupported-operator` errors on Python 3.9
- Never use `Optional[X]` — `ruff` (UP045) will flag it; use `X | None` instead

---

## Key Patterns

### Typing
- All function parameters and return types **must** be annotated
- Use `X | None` not `Optional[X]` (ruff UP045 rule)
- Use `from __future__ import annotations` (see above)
- Use `pydantic.SecretStr` for API keys passed to LangChain constructors

### Test-Driven Development
- Write a failing test → implement minimal code → make it pass
- Test file location mirrors source: `tests/adapters/llm/test_openai.py` for `src/langchat/adapters/llm/openai_provider.py`
- Test naming: `test_that_<context>_<action>_<expected_result>`
- Async tests: use `pytest-asyncio` with `asyncio_mode = "auto"` — no `@pytest.mark.asyncio` needed
- Engine/SDK tests: inherit from `SDKTest` base class

### Public API (`langchat.providers`)
```python
from langchat import LangChat
from langchat.providers import OpenAI, Pinecone, Supabase

lc = LangChat(
    llm=OpenAI("gpt-4o"),          # model is 1st positional arg
    vector_db=Pinecone("my-index"),
    db=Supabase(),
)

response = await lc.chat("Hello", user_id="alice", platform="app")
print(response.text)       # assistant reply
print(response.status)     # "success" | "error"
if response:               # True when status == "success"
    ...
```

### `ChatResponse` type
```python
@dataclass
class ChatResponse:
    text: str
    user_id: str
    platform: str
    status: Literal["success", "error"]
    response_time: float
    timestamp: str
    error: str | None = None

    def __bool__(self) -> bool: ...   # True on success
    def __str__(self) -> str: ...     # returns .text
```

### `platform` parameter
- Use `platform=` (not `domain=` — that was renamed)
- Groups conversations by logical namespace (e.g., `"web"`, `"mobile"`, `"default"`)

### Document indexing
```python
lc.index("docs/guide.pdf")                              # single file
lc.index(["docs/a.pdf", "docs/b.pdf"])                  # multiple files
lc.index("docs/guide.pdf", namespace="v2", chunk_size=500)
```

---

## Adding a New LLM Provider

1. Create `src/langchat/adapters/llm/<name>_provider.py` implementing the base LLM interface
2. Add a clean wrapper class in `src/langchat/providers/__init__.py` with auto-env-var loading
3. Export from `langchat/providers/__all__`
4. Add backward-compat re-export in `langchat/adapters/llm/__init__.py`
5. Write tests in `tests/adapters/llm/test_<name>_provider.py`
6. Document in `docs/providers/<name>.mdx`

---

## Version Bump Process

To release a new version (e.g., `1.0.3`):

1. Update `pyproject.toml`: `version = "1.0.3"`
2. Update `src/langchat/__init__.py`: `__version__ = "1.0.3"`
3. Update `tests/test_new_api.py`: `assert langchat.__version__ == "1.0.3"`
4. Update `CHANGELOG.md`: move `[Unreleased]` → `[1.0.3] — YYYY-MM-DD`, add new `[Unreleased]` section, update footer link
5. Run the full quality gate (format → lint → ty → pytest)
6. Commit with DCO sign-off: `git commit -s -m "chore: bump version to 1.0.3"`
7. Push to `develop`: `git push origin develop`
8. Merge `develop` → `main` to trigger the `publish.yml` GitHub Actions workflow → PyPI

---

## Branch & Release Workflow

```
develop  →  main  →  PyPI (automatic via publish.yml)
```

- All development happens on `develop`
- Merging `develop` into `main` triggers GitHub Actions to publish to PyPI
- Never commit directly to `main`

---

## Implementation Process

Before writing any code:

1. Read relevant existing source files for patterns (adapters, tests, interfaces)
2. Propose an implementation plan listing test file(s), class/function names, and approach
3. Wait for user confirmation
4. Write tests first — run them to confirm they fail
5. Implement minimal code to make tests pass
6. Run the full quality gate: `ruff format . && ruff check . --fix && ruff check . && unset VIRTUAL_ENV && ty check . && python -m pytest`
7. Commit with DCO sign-off: `git commit -s -m "<type>: <description>"`

---

## Documentation

Docs live in `docs/` in Mintlify `.mdx` format.

- Navigation config: `docs/mint.json`
- All code examples must use `langchat.providers` imports (not `langchat.adapters.*`)
- Use `platform=` parameter (not `domain=`)
- Use `response.text` (not `result["response"]`)
- Use `lc.index()` (not deprecated `load_and_index_documents()`)
- Python version in examples: 3.9+

### Mintlify components used in docs
```mdx
<Note>tip or info</Note>
<Warning>breaking or dangerous</Warning>
<CardGroup cols={2}>...</CardGroup>
<ParamField path="name" type="str" required>description</ParamField>
<CodeGroup>...</CodeGroup>
<Steps>...</Steps>
```

---

## Documentation References

When working on specific areas, read these files first:

| Area | File(s) to read |
|------|----------------|
| Core engine behavior | `src/langchat/core/engine.py` |
| Public SDK surface | `src/langchat/sdk.py`, `src/langchat/types.py` |
| Provider patterns | `src/langchat/providers/__init__.py` |
| Adapter structure | `src/langchat/adapters/llm/openai_provider.py` |
| API endpoints | `src/langchat/api/routes.py`, `src/langchat/api/models.py` |
| Test patterns | `tests/test_new_api.py`, any `tests/` file |
| Docs format | any existing `.mdx` file in `docs/` |
