# Contributing to LangChat

Thank you for your interest in contributing to LangChat! We welcome contributions from the community.

> **Important**: All contributions require a [Developer Certificate of Origin (DCO)](DCO.md) sign-off. See [Sign-off Process](#sign-off-process) below for details.

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

6. Commit your changes with DCO sign-off:
   ```bash
   git add .
   git commit -m "Description of your changes" -s
   ```
   
   **Important**: All commits must be signed off using the `-s` or `--signoff` flag to certify that you have the right to submit the code under the project's license. See [Sign-off Process](#sign-off-process) below for more details.

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

### Sign-off Process

All contributions to LangChat must include a Developer Certificate of Origin (DCO) sign-off. This certifies that you have the right to submit the code under the project's license.

#### What is DCO?

The Developer Certificate of Origin (DCO) is a lightweight way to certify that you wrote or have the right to submit the code you're contributing. It's based on the Linux Foundation's DCO, which is used by many open-source projects.

#### How to Sign Off Your Commits

**Option 1: Sign off when committing**
```bash
git commit -s -m "Your commit message"
```

**Option 2: Use --signoff flag**
```bash
git commit --signoff -m "Your commit message"
```

**Option 3: Add sign-off to the last commit**
If you forgot to sign off:
```bash
git commit --amend --signoff
```

**Option 4: Configure Git to auto-sign off**
```bash
git config --global commit.gpgsign false
git config --global format.signOff true
```

#### What Gets Added

When you sign off, Git automatically adds a "Signed-off-by" line to your commit message:

```
Your commit message

Signed-off-by: Your Name <your.email@example.com>
```

#### Example

```bash
git commit -s -m "Add feature to support custom reranker models"
```

This creates a commit message like:
```
Add feature to support custom reranker models

Signed-off-by: John Doe <john.doe@example.com>
```

#### Why is DCO Required?

- **Legal Protection**: Ensures you have the right to contribute the code
- **License Compliance**: Certifies the contribution meets license requirements
- **Project Integrity**: Maintains a clear chain of ownership
- **Industry Standard**: Used by many major open-source projects (Linux Kernel, Kubernetes, etc.)

#### DCO Verification

Your Pull Request will be checked for DCO sign-off. If your commits don't have sign-off, you'll need to add it before the PR can be merged.

**Check if your commits are signed off:**
```bash
git log --show-signature
```

**Fix unsigned commits:**
```bash
# For the last commit
git commit --amend --signoff --no-edit

# For multiple commits (interactive rebase)
git rebase -i HEAD~n  # Replace n with number of commits
# Change 'pick' to 'edit' for commits that need sign-off
# Then for each commit:
git commit --amend --signoff --no-edit
git rebase --continue
```

#### Troubleshooting

**Q: I forgot to sign off a commit, what do I do?**
A: Use `git commit --amend --signoff --no-edit` for the last commit, or rebase to fix multiple commits.

**Q: Can I sign off on behalf of someone else?**
A: No, only the author of the code can sign off. If you're incorporating someone else's work, they must sign off first, or you must have explicit permission.

**Q: Do I need to sign off on every commit?**
A: Yes, every commit in your PR must be signed off.

**Q: What if I'm contributing a small fix?**
A: Even small fixes require sign-off. It's a quick process - just add `-s` to your commit command.

#### More Information

- Read the full [DCO.md](DCO.md) document
- Learn more at [developercertificate.org](https://developercertificate.org/)

### Review Process

1. Maintainers will review your PR
2. DCO sign-off will be verified on all commits
3. We may request changes or provide feedback
4. Once approved, your PR will be merged
5. Thank you for contributing! 🎉

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

