#!/usr/bin/env python3
"""
Setup script for SolvIQ RAG System
"""

from setuptools import setup, find_packages
import os
import sys
from pathlib import Path

# Read the README file
def read_readme():
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return "SolvIQ RAG System for Solution Engineers"

# Read requirements from pyproject.toml
def read_requirements():
    """Read requirements from pyproject.toml"""
    requirements = [
        "langchain>=0.3.19",
        "langchain-community>=0.3.16", 
        "langchain-openai>=0.3.28",
        "openai>=1.99.2",
        "tavily-python>=0.5.0",
        "faiss-cpu>=1.12.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "streamlit>=1.50.0",
        "requests>=2.32.3",
        "httpx>=0.24.0",
        "python-dotenv>=1.0.1",
        "pydantic>=2.0.0",
        "numpy>=2.0.0",
        "pandas>=2.0.0",
        "ragas>=0.2.10",
        "structlog>=23.0.0"
    ]
    return requirements

setup(
    name="solviq-rag",
    version="1.0.0",
    description="AI-powered RAG system for Solution Engineers and M&A teams",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Vijaya Tirumalareddy",
    author_email="vijaya@example.com",
    url="https://github.com/vijaya-tirumala/AIE8-cert-challenge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.11",
    # install_requires=read_requirements(),  # Defined in pyproject.toml
    # extras_require={
    #     "dev": ["mypy>=1.11.1", "ruff>=0.6.1", "pytest>=7.0.0"],
    # },
    # entry_points={
    #     "console_scripts": [
    #         "solviq-setup=solviq.setup:main",
    #     ],
    # },
    include_package_data=True,
    zip_safe=False,
)
