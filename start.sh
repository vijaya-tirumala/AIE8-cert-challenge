#!/bin/bash

# SolvIQ Interactive Startup Script
echo "⚡ Starting SolvIQ Application..."
echo "The intelligence layer for every Solution Engineer."

# Function to cleanup existing processes
cleanup_ports() {
    echo "🧹 Cleaning up existing processes on ports 8000 and 8501..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8501 | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project root directory."
    exit 1
fi

# Cleanup existing processes
cleanup_ports

# Function to get API keys interactively
get_api_keys() {
    echo "🔑 API Key Setup Required"
    echo "========================="
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "🔑 Please enter your OpenAI API Key:"
        echo "   (You can get it from: https://platform.openai.com/account/api-keys)"
        read -s -p "Enter OpenAI API Key (hidden): " OPENAI_API_KEY
        echo ""
        if [ -z "$OPENAI_API_KEY" ]; then
            echo "❌ OpenAI API Key is required!"
            echo "Please set it manually with: export OPENAI_API_KEY='your_key'"
            exit 1
        fi
        export OPENAI_API_KEY
        echo "✅ OpenAI API Key set"
    else
        echo "✅ OpenAI API Key found"
    fi
    
    echo ""
    if [ -z "$TAVILY_API_KEY" ]; then
        echo "🔑 Please enter your Tavily API Key:"
        echo "   (You can get it from: https://tavily.com/)"
        read -s -p "Enter Tavily API Key (hidden): " TAVILY_API_KEY
        echo ""
        if [ -z "$TAVILY_API_KEY" ]; then
            echo "❌ Tavily API Key is required!"
            echo "Please set it manually with: export TAVILY_API_KEY='your_key'"
            exit 1
        fi
        export TAVILY_API_KEY
        echo "✅ Tavily API Key set"
    else
        echo "✅ Tavily API Key found"
    fi
    
    echo ""
    echo "🚀 Ready to start SolvIQ with API keys!"
    echo "========================================"
}

# Get API keys
get_api_keys

# Install frontend dependencies if needed
echo "📦 Installing frontend dependencies..."
uv add streamlit fastapi uvicorn requests

# Verify API keys are set
if [ -z "$OPENAI_API_KEY" ] || [ -z "$TAVILY_API_KEY" ]; then
    echo "❌ Error: API keys are not properly set!"
    exit 1
fi

# Start FastAPI backend in background
echo "🧠 Starting SolvIQ API backend on port 8000..."
echo "🔑 Using OpenAI API Key: ${OPENAI_API_KEY:0:10}..."
echo "🔑 Using Tavily API Key: ${TAVILY_API_KEY:0:10}..."
echo ""

# Export environment variables and start backend
export OPENAI_API_KEY
export TAVILY_API_KEY
source .venv/bin/activate && python -m uvicorn app:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend started successfully"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID
    exit 1
fi

# Start Streamlit frontend
echo "🎨 Starting SolvIQ frontend on port 8501..."
echo "🌐 Frontend will be available at: http://localhost:8501"
echo "📚 API docs will be available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID
    exit 0
}

# Set trap for cleanup
trap cleanup INT

# Start frontend
source .venv/bin/activate && python -m streamlit run frontend.py --server.port 8501
