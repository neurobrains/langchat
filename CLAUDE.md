# LangChat - Production-Grade AI Chatbot Framework

## Project Overview
LangChat is a Python library for building enterprise-scale AI chatbots with built-in conversational management, designed for production use where SLAs, stability, and security are critical.

Repository: https://github.com/neurobrains/langchat

## Architecture
**Hexagonal Architecture (Ports and Adapters)**
```
src/langchat/
├── core/       # Framework core (domain logic, interfaces)
├── adapters/   # 3rd-party tool implementations
└── api/        # FastAPI REST layer (uses core/)

tests/          # Mirrors src/langchat structure
```

## Tech Stack
- **Language:** Python (strict MyPy type checking)
- **Testing:** pytest, TDD workflow
- **Linting:** ruff formatter
- **API:** FastAPI

## Development Workflow
```bash
# Run specific test
python -m pytest tests/path/to/test.py::test_name

# Format code (run before committing)
ruff format .

# Lint check
python -m scripts/lint.py --ty --ruff
```

## Key Patterns
1. **Strict typing:** All parameters and return types must be annotated
2. **TDD:** Write failing test → implement minimal code → pass test
3. **Test naming:** `test_that_<context>_<action>_<expected_result>`
4. **SDK testing:** Inherit from `SDKTest` for engine behavior tests
5. **Hexagonal boundaries:** Keep core/ independent, adapters implement interfaces

## Documentation References
When working on specific areas, read these files first:
- Architecture details: `docs/architecture.md` (if exists)
- API patterns: Check existing `src/langchat/api/` endpoints
- Adapter examples: Review `src/langchat/adapters/` implementations
- Test patterns: See `tests/` for SDKTest usage examples

## Implementation Process
Before coding, always:
1. Analyze codebase structure for similar patterns
2. Propose implementation plan with test files/names
3. Wait for plan confirmation
4. Write tests first, get review
5. Implement code to pass tests
6. Format with ruff and run lint checks
