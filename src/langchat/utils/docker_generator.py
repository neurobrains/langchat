"""
Auto-generate Dockerfile, .dockerignore, and requirements.txt for LangChat.
"""

import ast
from pathlib import Path


def generate_dockerfile(
    output_path: str = "Dockerfile",
    port: int = 8000,
    python_version: str = "3.11",
    app_file: str = "main.py",
) -> str:
    """
    Generate Dockerfile for LangChat.

    Args:
        output_path: Path to save the Dockerfile
        port: Port number for the application
        python_version: Python version to use
        app_file: Main application file

    Returns:
        Path to generated file
    """
    dockerfile_content = f"""# LangChat Dockerfile
FROM python:{python_version}-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE {port}

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT={port}

# Run the application
CMD ["python", "{app_file}"]
"""

    Path(output_path).write_text(dockerfile_content, encoding="utf-8")

    return output_path


def generate_dockerignore(output_path: str = ".dockerignore") -> str:
    """
    Generate .dockerignore file for LangChat.

    Args:
        output_path: Path to save the .dockerignore file

    Returns:
        Path to generated file
    """
    dockerignore_content = """# Git
.git
.gitignore
.gitattributes

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.hypothesis/

# Environment variables
.env
.env.local
.env.*.local

# Logs
*.log
*.csv

# Documentation
docs/_build/
*.html

# OS
Thumbs.db
.DS_Store

# Project specific
examples/
tests/
*.md
README.md
LICENSE
"""

    Path(output_path).write_text(dockerignore_content, encoding="utf-8")

    return output_path


def extract_dependencies_from_setup(setup_path: str = "setup.py") -> list:
    """
    Extract dependencies from setup.py file.

    Args:
        setup_path: Path to setup.py file

    Returns:
        List of dependency strings
    """
    dependencies = []

    try:
        setup_path_obj = Path(setup_path)
        if setup_path_obj.exists():
            content = setup_path_obj.read_text(encoding="utf-8")

            # Parse setup.py to extract install_requires
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "setup"
                ):
                    for keyword in node.keywords:
                        if keyword.arg == "install_requires" and isinstance(
                            keyword.value, ast.List
                        ):
                            for item in keyword.value.elts:
                                # Skip comments (they appear as Constant or Str with #)
                                if isinstance(item, ast.Constant):
                                    value = item.value
                                    if isinstance(value, str) and not value.strip().startswith("#"):
                                        dependencies.append(value)
                                elif isinstance(item, ast.Str):  # Python < 3.8 compatibility
                                    value = item.s
                                    if isinstance(value, str) and not value.strip().startswith("#"):
                                        dependencies.append(value)
        else:
            # If setup.py doesn't exist, use default dependencies
            dependencies = [
                "fastapi==0.115.14",
                "uvicorn==0.34.3",
                "starlette==0.46.2",
                "pydantic==2.11.7",
                "python-multipart==0.0.20",
                "pytz==2022.7",
                "requests==2.32.3",
                "langchain==0.3.27",
                "langchain-core>=0.1.0",
                "langchain-pinecone>=0.1.0",
                "langchain-community>=0.0.20",
                "langchain-openai>=0.1.0",
                "openai>=1.0.0",
                "tiktoken==0.9.0",
                "pinecone-client>=3.0.0",
                "flashrank==0.2.10",
                "supabase==2.15.2",
            ]
    except Exception:
        # Fallback to default dependencies if parsing fails
        dependencies = [
            "fastapi==0.115.14",
            "uvicorn==0.34.3",
            "starlette==0.46.2",
            "pydantic==2.11.7",
            "python-multipart==0.0.20",
            "pytz==2022.7",
            "requests==2.32.3",
            "langchain==0.3.27",
            "langchain-core>=0.1.0",
            "langchain-pinecone>=0.1.0",
            "langchain-community>=0.0.20",
            "langchain-openai>=0.1.0",
            "openai>=1.0.0",
            "tiktoken==0.9.0",
            "pinecone-client>=3.0.0",
            "flashrank==0.2.10",
            "supabase==2.15.2",
        ]

    return dependencies


def generate_requirements_txt(
    output_path: str = "requirements.txt", setup_path: str = "setup.py"
) -> str:
    """
    Generate requirements.txt file from setup.py or use defaults.

    Args:
        output_path: Path to save the requirements.txt file
        setup_path: Path to setup.py file to read dependencies from

    Returns:
        Path to generated file
    """
    dependencies = extract_dependencies_from_setup(setup_path)

    # Format dependencies with comments - organize by category
    web_framework = []
    core_func = []
    langchain_openai = []
    vector_db = []
    reranker = []
    supabase = []
    other = []

    for dep in dependencies:
        dep_lower = dep.lower()
        if any(
            kw in dep_lower for kw in ["fastapi", "uvicorn", "starlette", "pydantic", "multipart"]
        ):
            web_framework.append(dep)
        elif any(kw in dep_lower for kw in ["pytz", "requests"]):
            core_func.append(dep)
        elif any(kw in dep_lower for kw in ["langchain", "openai", "tiktoken"]):
            langchain_openai.append(dep)
        elif "pinecone" in dep_lower:
            vector_db.append(dep)
        elif "flashrank" in dep_lower:
            reranker.append(dep)
        elif "supabase" in dep_lower:
            supabase.append(dep)
        else:
            other.append(dep)

    # Build requirements content
    requirements_content = ""

    if web_framework:
        requirements_content += "# Core app & web framework\n"
        requirements_content += "\n".join(web_framework) + "\n\n"

    if core_func:
        requirements_content += "# Core functionality\n"
        requirements_content += "\n".join(core_func) + "\n\n"

    if langchain_openai:
        requirements_content += "# LangChain & OpenAI\n"
        requirements_content += "\n".join(langchain_openai) + "\n\n"

    if vector_db:
        requirements_content += "# Vector DBs\n"
        requirements_content += "\n".join(vector_db) + "\n\n"

    if reranker:
        requirements_content += "# Flashrank reranker\n"
        requirements_content += "\n".join(reranker) + "\n\n"

    if supabase:
        requirements_content += "# Supabase\n"
        requirements_content += "\n".join(supabase) + "\n\n"

    if other:
        requirements_content += "# Other dependencies\n"
        requirements_content += "\n".join(other) + "\n"

    # Remove trailing newlines
    requirements_content = requirements_content.strip() + "\n"

    Path(output_path).write_text(requirements_content, encoding="utf-8")

    return output_path


def generate_all_docker_files(
    output_dir: str = ".",
    port: int = 8000,
    python_version: str = "3.11",
    app_file: str = "main.py",
) -> dict:
    """
    Generate all Docker-related files: Dockerfile, .dockerignore, and requirements.txt.

    Args:
        output_dir: Directory to save the files
        port: Port number for the application
        python_version: Python version to use
        app_file: Main application file

    Returns:
        Dictionary with paths to generated files
    """
    output_dir_path = Path(output_dir)

    dockerfile_path = generate_dockerfile(
        output_path=str(output_dir_path / "Dockerfile"),
        port=port,
        python_version=python_version,
        app_file=app_file,
    )

    dockerignore_path = generate_dockerignore(output_path=str(output_dir_path / ".dockerignore"))

    requirements_path = generate_requirements_txt(
        output_path=str(output_dir_path / "requirements.txt"),
        setup_path=str(output_dir_path / "setup.py"),
    )

    return {
        "dockerfile": dockerfile_path,
        "dockerignore": dockerignore_path,
        "requirements": requirements_path,
    }
