# Contributing to LangChat

Thank you for your interest in contributing to LangChat! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Environment details (Python version, OS, etc.)
- Any relevant error messages or logs

### Suggesting Features

We welcome feature suggestions! Please open an issue with:
- A clear description of the feature
- Use cases and examples
- Why this feature would be useful

### Code Contributions

#### Setting Up Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/LangChat.git
   cd LangChat
   ```
3. Install in development mode:
   ```bash
   pip install -e .
   ```
4. Install development dependencies:
   ```bash
   pip install pytest pytest-asyncio black flake8 mypy
   ```

#### Development Workflow

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. Make your changes following our coding standards:
   - Follow PEP 8 style guide
   - Add type hints where appropriate
   - Write docstrings for functions and classes
   - Keep functions focused and small

3. Run tests:
   ```bash
   pytest
   ```

4. Run code formatting:
   ```bash
   black src/
   ```

5. Run linting:
   ```bash
   flake8 src/
   ```

6. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

7. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

8. Create a Pull Request on GitHub

#### Coding Standards

- **Python Style**: Follow PEP 8
- **Type Hints**: Use type hints for function parameters and return types
- **Docstrings**: Use Google-style docstrings
- **Naming**: Use descriptive names, follow Python naming conventions
- **Error Handling**: Handle errors gracefully with appropriate exceptions

#### Code Structure

The project follows a modular architecture:
- `src/langchat/adapters/` - External service adapters
- `src/langchat/core/` - Core business logic
- `src/langchat/api/` - FastAPI routes and app
- `src/langchat/utils/` - Utility functions

When adding new features:
- Keep modules focused and cohesive
- Follow existing patterns
- Add appropriate tests
- Update documentation

#### Writing Tests

- Add tests for new features
- Ensure existing tests pass
- Aim for good test coverage
- Use pytest and pytest-asyncio for async tests

Example test:
```python
import pytest
from langchat.config import LangChatConfig

def test_config_creation():
    config = LangChatConfig(
        openai_api_keys=["test-key"],
        pinecone_api_key="test-key",
        pinecone_index_name="test-index",
        supabase_url="test-url",
        supabase_key="test-key"
    )
    assert config.openai_model == "gpt-4o-mini"
```

#### Documentation

- Update README.md if adding new features
- Add docstrings to new functions/classes
- Update relevant documentation files
- Add examples if applicable

#### Pull Request Guidelines

1. **Clear Title**: Summarize your changes in the title
2. **Description**: Explain what and why you changed
3. **Tests**: Ensure all tests pass
4. **Documentation**: Update relevant docs
5. **Breaking Changes**: Clearly mark any breaking changes

Example PR description:
```markdown
## Description
Adds support for custom reranker models.

## Changes
- Added `reranker_model` parameter to LangChatConfig
- Updated FlashrankRerankAdapter to use custom models
- Added tests for custom reranker

## Testing
- [x] All existing tests pass
- [x] New tests added for custom reranker
- [x] Tested with different reranker models

## Documentation
- [x] Updated README.md
- [x] Updated config documentation
```

### Review Process

1. Maintainers will review your PR
2. We may request changes or provide feedback
3. Once approved, your PR will be merged
4. Thank you for contributing! 🎉

## Questions?

If you have questions about contributing:
- Open an issue for discussion
- Check existing issues and PRs
- Review the codebase to understand patterns

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards others

Thank you for making LangChat better! 🚀

