"""
Setup script for LangChat package.
"""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="langchat",
    version="1.0.0",
    author="Sifat Hasan <sihabhossan633@gmail.com>, NeuroBrain",
    author_email="contact@neurobrain.co",
    description="A conversational AI library with vector search capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neurobrains/langchat",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi==0.115.14",
        "uvicorn==0.34.3",
        "starlette==0.46.2",
        "pydantic==2.11.7",
        "python-multipart==0.0.20",
        "pytz==2022.7",
        "requests==2.32.3",
        # LangChain packages
        "langchain==0.3.27",
        "langchain-core>=0.3.72,<1.0.0",  # langchain==0.3.27 requires this range
        "langchain-pinecone>=0.1.0,<0.3.0",
        "langchain-community>=0.3.0,<0.4.0",
        "langchain-openai>=0.2.0,<0.3.0",
        "openai>=1.0.0",
        "tiktoken==0.9.0",
        "pinecone-client>=3.0.0",
        "flashrank==0.2.10",
        "supabase==2.15.2",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
)
