#!/bin/bash
# Quick start script for Visara

set -e

echo "🚀 Visara - Network Outage Analyzer"
echo "===================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Show Python version
PY_VERSION=$(python3 --version)
echo "✅ Found: $PY_VERSION"
echo ""

# Test setup
echo "🔍 Verifying setup..."
python3 test_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All checks passed!"
    echo ""
    echo "Choose an option:"
    echo "  1) Run CLI (generate a report)"
    echo "  2) Start web server (API + Frontend)"
    echo "  3) Test MCP server (requires Python 3.10+)"
    echo "  4) Exit"
    echo ""
    read -p "Enter choice [1-4]: " choice
    
    case $choice in
        1)
            echo ""
            echo "🔧 Running CLI..."
            python3 main.py
            ;;
        2)
            echo ""
            echo "🌐 Starting web server..."
            echo "   API will run on http://localhost:8000"
            echo "   Press Ctrl+C to stop"
            echo ""
            uvicorn server.app:app --reload
            ;;
        3)
            echo ""
            echo "🔧 Testing MCP server..."
            python3 mcp_server.py
            ;;
        4)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice"
            exit 1
            ;;
    esac
else
    echo ""
    echo "❌ Setup verification failed"
    echo "   Run: pip install -r requirements.txt"
    exit 1
fi

