#!/usr/bin/env python3
"""
Setup check script for SolvIQ RAG System
"""

import os
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import uv
        print("✅ uv package manager found")
    except ImportError:
        print("⚠️  uv package manager not found. You can install it with: pip install uv")
        print("   Or use pip directly to install dependencies")


def check_data_directory():
    """Check if data directory exists"""
    data_path = Path("data")
    if not data_path.exists():
        print("❌ Data directory not found")
        sys.exit(1)
    
    md_files = list(data_path.glob("*.md"))
    if not md_files:
        print("❌ No markdown files found in data directory")
        sys.exit(1)
    
    print(f"✅ Found {len(md_files)} markdown files in data directory")


def check_environment():
    """Check environment variables"""
    required_vars = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before running the application")
    else:
        print("✅ All required environment variables are set")


def main():
    """Main setup function"""
    print("🔧 SolvIQ Setup Check")
    print("=" * 30)
    
    check_python_version()
    check_dependencies()
    check_data_directory()
    check_environment()
    
    print("\n🎉 Setup check complete!")
    print("Run './start.sh' to start the application")


if __name__ == "__main__":
    main()
