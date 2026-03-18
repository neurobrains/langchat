# Changelog

All notable changes to LangChat are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added

**`langchat.providers` — new clean public API module**
- Single import for all providers: `from langchat.providers import OpenAI, Pinecone, Supabase`
- All providers auto-read credentials from environment variables; explicit keys are optional overrides
- Model name is the **first positional argument** (`OpenAI("gpt-4o")`, `Pinecone("my-index")`) — no more verbose keyword constructors
- Clear `ValueError` messages that name the exact environment variable when a key is missing
- `Gemini` accepts `GEMINI_API_KEY` or `GOOGLE_API_KEY` as fallback
- `Supabase` accepts `SUPABASE_KEY` or `SUPABASE_SERVICE_ROLE_KEY` as fallback
- `Ollama` requires no API key (self-hosted)

**`langchat.types.ChatResponse` — typed return value**
- `LangChat.chat()` now returns a `ChatResponse` dataclass instead of a raw `dict`
- Fields: `text`, `user_id`, `platform`, `status`, `response_time`, `timestamp`, `error`
- `bool(response)` → `True` when success, `False` on error
- `str(response)` → `response.text` (works directly with `print()` and f-strings)
- `response.error` is `str | None`, populated only on failure

**`LangChat.index()` — unified document indexing**
- Replaces `load_and_index_documents()` + `load_and_index_multiple_documents()`
- Single method accepts a `str` (one file) or `list[str]` (many files)
- All existing options (`chunk_size`, `chunk_overlap`, `namespace`, `prevent_duplicates`) unchanged

**Package-level imports**
- `ChatResponse` now importable directly from `langchat`: `from langchat import ChatResponse`
- `providers` accessible as `langchat.providers` via lazy `__getattr__` — optional dependencies are not imported until the submodule is actually used

**Developer tooling (migration from Poetry → uv)**
- Migrated to [uv](https://docs.astral.sh/uv/) for 10–100× faster dependency resolution
- `pyproject.toml` updated: removed `poetry-core` build requirement, added `[tool.uv]`
- `poetry.toml` removed
- `python-dotenv` added as explicit dependency (was previously implicit)
- `requires-python` bumped from `>=3.8` to `>=3.9`
- `pytest` and `ruff` version floors raised to `>=8.0.0` and `>=0.4.0` respectively
- Project URL table added to `pyproject.toml` (Homepage, Repository, Docs, Bug Tracker, Changelog)

**Examples — real-life use cases**
- `examples/basic.py` — customer-support chatbot with per-user sessions
- `examples/custom_prompt.py` — internal HR knowledge base with custom system prompt and tone rules
- `examples/server.py` — production FastAPI server (simplified to new API)
- `examples/rag_indexing.py` *(new)* — document indexing patterns: single file, folder scan, per-department namespaces
- `examples/multi_provider.py` *(new)* — concurrent A/B testing of multiple LLM providers

**Tests**
- `tests/test_types.py` — 23 tests for `ChatResponse` (fields, `bool`, `str`, dataclass protocol)
- `tests/providers/test_providers.py` — 44 tests covering all 8 providers: explicit keys, env-var fallback, missing-key errors, positional arg
- **175 tests total, 0 failures**

### Changed

- `LangChat.chat()` return type changed from `dict` → `ChatResponse`
  - Use `response.text` instead of `result["response"]`
- `LangChat.load_and_index_documents()` and `load_and_index_multiple_documents()` are **deprecated** in favour of `LangChat.index()` (both still work)
- `CONTRIBUTING.md` rewritten with uv setup instructions, updated PR checklist, provider extension guide
- README rewritten: new API quick-start, provider cheat-sheet, typed response docs, `index()` usage
- Existing adapter code updated to modern Python 3.9+ type syntax (`list[...]`, `dict[...]` instead of `List`, `Dict`)

### Deprecated

- `LangChat.load_and_index_documents(file_path, ...)` — use `LangChat.index(path, ...)` instead
- `LangChat.load_and_index_multiple_documents(file_paths, ...)` — use `LangChat.index(paths, ...)` instead

### Removed

- `setup.py` — superseded by `pyproject.toml` (PEP 621)
- `poetry.toml` — superseded by uv

### Fixed

- Lazy `providers` import in `langchat/__init__.py` prevents `ModuleNotFoundError` when optional adapter dependencies are not installed and the user only imports `LangChat`
- Recursion guard in `langchat.__getattr__`: uses `import langchat.providers` instead of the recursive `from langchat import providers`
- All ruff lint warnings resolved across `src/` and `tests/`

---

## [1.0.1] — 2025-01-15

### Fixed

- Various bug fixes and stability improvements

### Removed

- Agent system (removed in favour of simpler SDK approach)
- Multi-agent system
- RAG agent system
- Tool system

### Added

- Provider system with support for OpenAI, Anthropic, Gemini, Mistral, Cohere, Ollama
- Auto-detection of provider types
- Clean import structure
- Intuitive API surface
- Better type hints throughout
- Async / sync support
- API key rotation logic for resilience
- Improved error handling
- Optimised provider initialisation
- Better connection pooling
- Reduced memory footprint

---

[Unreleased]: https://github.com/neurobrains/langchat/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/neurobrains/langchat/compare/v1.0.0...v1.0.1
