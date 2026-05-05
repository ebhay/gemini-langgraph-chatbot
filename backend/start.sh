#!/bin/bash

echo "Starting Gemini Chatbot Backend..."
echo ""

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run setup.sh first"
    exit 1
fi

source venv/bin/activate

echo "Checking environment variables..."
python -c "from config import settings; print('✓ GEMINI_API_KEY:', 'SET' if settings.GEMINI_API_KEY else 'NOT SET'); print('✓ JWT_SECRET_KEY:', 'SET' if settings.JWT_SECRET_KEY else 'NOT SET')"

echo ""
echo "Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

python run.py
