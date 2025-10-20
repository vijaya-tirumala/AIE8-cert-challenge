#!/usr/bin/env python3
"""
Get API keys interactively for SolvIQ
"""

import os
import sys
import getpass

def get_api_keys():
    """Get API keys from user input"""
    print("🔑 API Key Setup Required")
    print("=========================")
    
    # Get OpenAI API Key
    if not os.environ.get("OPENAI_API_KEY"):
        print("🔑 Please enter your OpenAI API Key:")
        print("   (You can get it from: https://platform.openai.com/account/api-keys)")
        openai_key = input("Enter OpenAI API Key: ").strip()
        
        if not openai_key:
            print("❌ OpenAI API Key is required!")
            print("Please set it manually with: export OPENAI_API_KEY='your_key'")
            sys.exit(1)
        
        os.environ["OPENAI_API_KEY"] = openai_key
        print("✅ OpenAI API Key set")
    else:
        print("✅ OpenAI API Key found")
    
    print("")
    
    # Get Tavily API Key
    if not os.environ.get("TAVILY_API_KEY"):
        print("🔑 Please enter your Tavily API Key:")
        print("   (You can get it from: https://tavily.com/)")
        tavily_key = input("Enter Tavily API Key: ").strip()
        
        if not tavily_key:
            print("❌ Tavily API Key is required!")
            print("Please set it manually with: export TAVILY_API_KEY='your_key'")
            sys.exit(1)
        
        os.environ["TAVILY_API_KEY"] = tavily_key
        print("✅ Tavily API Key set")
    else:
        print("✅ Tavily API Key found")
    
    print("")
    print("🚀 Ready to start SolvIQ with API keys!")
    print("========================================")
    
    return os.environ["OPENAI_API_KEY"], os.environ["TAVILY_API_KEY"]

if __name__ == "__main__":
    get_api_keys()
