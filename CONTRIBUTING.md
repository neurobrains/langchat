# Contributing to LangChat

First off, thank you for considering contributing to LangChat! Whether you're fixing a bug, adding a feature, or improving documentation, your help makes this project better for everyone.


## 1. Getting Started in 3 Steps

### Setup Your Environment

```bash
# Fork & Clone
git clone https://github.com/your-username/LangChat.git && cd LangChat

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```
---

### 2. Development Workflow

Always create a new branch for your work:
- Features: `feature/awesome-new-capability`
- Fixes: `fix/resolved-issue-name`

### Before committing, ensure your code stays sharp
- Format: `ruff check .`
- Test: `pytest`

---

### 3. The "Golden Rule": DCO Sign-off

To maintain project integrity, all commits must be signed off. It’s as simple as adding `-s` to your commit command.

```bash
git commit -s -m "Brief description of your amazing work"
```
This adds `Signed-off-by: Your Name <email>` to your message, certifying your contribution.

---

# Project Architecture

Keep your contributions modular by following our directory structure:

|    Module          |                          Responsibility                         |
|--------------------|-----------------------------------------------------------------|
| `adapters/`        |  External service integrations (OpenAI, Pinecone, etc.)         |
| `core/`            |  Logic for chat, memory, and orchestration.                     |
| `api/`             |  FastAPI implementation and routes.                             |
| `utils/`           |  Shared helpers and formatting.                                 |

---

# ✅ Pull Request Checklist
Before you hit "Create Pull Request," make sure:
- [ ] Your code follows PEP 8 and includes type hints.
- [ ] You’ve added/updated tests for your changes.
- [ ] Every commit has the -s sign-off.
- [ ] The documentation (README or docstrings) is updated.

---

# Have an Idea or Found a Bug?

- Bugs: Open an issue with a clear description and steps to reproduce.
- Features: Start a discussion in Issues. We love bold ideas!

---

# Let's Build the Future of AI Together.

Your contributions help developers worldwide ship production-ready AI faster. We can't wait to see what you build!

<p style="margin-top: 15px;">
  <a href="https://github.com/neurobrains/langchat/issues">Open an Issue</a> • 
  <a href="https://langchat.neurobrains.co/">Documentation</a>
</p>
