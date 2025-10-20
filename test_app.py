#!/usr/bin/env python3
"""
Test script to verify the RAG application setup
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from rag_components import RAGConfig, DocumentProcessor, VectorStoreManager
        print("✅ RAG components imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import RAG components: {e}")
        return False
    
    try:
        import fastapi
        import uvicorn
        import streamlit
        print("✅ Web framework dependencies imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import web framework dependencies: {e}")
        return False
    
    return True

def test_data_directory():
    """Test that data directory exists and contains files"""
    print("\n📁 Testing data directory...")
    
    from config import get_data_path
    data_path = get_data_path()
    
    if not data_path.exists():
        print(f"❌ Data directory not found: {data_path}")
        return False
    
    md_files = list(data_path.glob("*.md"))
    if not md_files:
        print(f"❌ No markdown files found in data directory")
        return False
    
    print(f"✅ Found {len(md_files)} markdown files in data directory")
    for file in md_files:
        print(f"   📄 {file.name}")
    
    return True

def test_api_keys():
    """Test API key configuration"""
    print("\n🔑 Testing API key configuration...")
    
    openai_key = os.environ.get("OPENAI_API_KEY")
    tavily_key = os.environ.get("TAVILY_API_KEY")
    
    if not openai_key:
        print("⚠️  OPENAI_API_KEY not set")
    else:
        print("✅ OPENAI_API_KEY is set")
    
    if not tavily_key:
        print("⚠️  TAVILY_API_KEY not set")
    else:
        print("✅ TAVILY_API_KEY is set")
    
    if not openai_key or not tavily_key:
        print("\n💡 To set API keys:")
        print("   export OPENAI_API_KEY='your-openai-key'")
        print("   export TAVILY_API_KEY='your-tavily-key'")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing SE RAG Agent Application Setup")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Data Directory", test_data_directory),
        ("API Keys", test_api_keys)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The application is ready to run.")
        print("\n🚀 To start the application:")
        print("   1. Set your API keys")
        print("   2. Run: ./start_app_interactive.sh")
        print("   3. Or manually:")
        print("      - Backend: uvicorn app:app --reload --port 8000")
        print("      - Frontend: streamlit run frontend.py --server.port 8501")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
