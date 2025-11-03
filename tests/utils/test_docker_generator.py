"""
Tests for docker_generator utility.
"""

import pytest
from unittest.mock import patch, mock_open
from pathlib import Path
from langchat.utils.docker_generator import (
    generate_dockerfile,
    generate_dockerignore,
    extract_dependencies_from_setup,
)


class TestDockerGenerator:
    """Test cases for docker_generator."""

    def test_generate_dockerfile_exists(self):
        """Test that generate_dockerfile function exists."""
        assert callable(generate_dockerfile)

    def test_generate_dockerfile_creates_file(self, tmp_path):
        """Test that generate_dockerfile creates a file."""
        output_file = tmp_path / "Dockerfile"
        
        result = generate_dockerfile(
            output_path=str(output_file),
            port=8000,
            python_version="3.11",
        )
        
        assert result == str(output_file)
        assert output_file.exists()
        assert output_file.read_text()
        assert "FROM python:3.11-slim" in output_file.read_text()

    def test_generate_dockerfile_custom_port(self, tmp_path):
        """Test generate_dockerfile with custom port."""
        output_file = tmp_path / "Dockerfile"
        
        generate_dockerfile(
            output_path=str(output_file),
            port=9000,
        )
        
        content = output_file.read_text()
        assert "EXPOSE 9000" in content

    def test_generate_dockerignore_exists(self):
        """Test that generate_dockerignore function exists."""
        assert callable(generate_dockerignore)

    def test_generate_dockerignore_creates_file(self, tmp_path):
        """Test that generate_dockerignore creates a file."""
        output_file = tmp_path / ".dockerignore"
        
        result = generate_dockerignore(output_path=str(output_file))
        
        assert result == str(output_file)
        assert output_file.exists()
        content = output_file.read_text()
        assert "__pycache__" in content or "__pycache__/" in content

    def test_extract_dependencies_from_setup_exists(self):
        """Test that extract_dependencies_from_setup function exists."""
        assert callable(extract_dependencies_from_setup)

    def test_extract_dependencies_from_setup(self, tmp_path):
        """Test extracting dependencies from setup.py."""
        setup_file = tmp_path / "setup.py"
        setup_file.write_text("""
from setuptools import setup
setup(
    install_requires=[
        "fastapi==0.115.14",
        "uvicorn==0.34.3",
    ]
)
        """)
        
        deps = extract_dependencies_from_setup(str(setup_file))
        
        assert isinstance(deps, list)
        assert len(deps) > 0
        assert any("fastapi" in dep for dep in deps)

