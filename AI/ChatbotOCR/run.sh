#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "🤖 Support Screenshot Chatbot - Quick Start Runner"
echo "============================================================"

# 1. Determine Python command
PYTHON_BIN="python3"
if ! command -v "$PYTHON_BIN" &> /dev/null; then
    PYTHON_BIN="python"
fi

if ! command -v "$PYTHON_BIN" &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH."
    exit 1
fi

# 2. Check or create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment in ./venv..."
    "$PYTHON_BIN" -m venv venv
    echo "📥 Installing dependencies from requirements.txt..."
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
fi

# 3. Check .env configuration
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "⚙️ Creating .env from .env.example..."
        cp .env.example .env
    fi
fi

# 4. Start the Application Server
echo ""
echo "🚀 Starting ChatbotOCR Web Application..."
echo "👉 Web Chat UI:        http://localhost:8000"
echo "👉 Swagger API Docs:   http://localhost:8000/docs"
echo "============================================================"
exec ./venv/bin/python main.py server --host 0.0.0.0 --port 8000
