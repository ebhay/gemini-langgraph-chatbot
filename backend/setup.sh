#!/bin/bash

echo "=== Gemini LangGraph Chatbot Backend Setup ==="
echo ""

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your credentials:"
    echo "   - GEMINI_API_KEY"
    echo "   - JWT_SECRET_KEY (generate with: python -c 'import secrets; print(secrets.token_hex(32))')"
    echo "   - SMTP_USER (your Gmail address)"
    echo "   - SMTP_PASSWORD (Gmail app password)"
    echo "   - SMTP_FROM_EMAIL (your Gmail address)"
    echo ""
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run: python run.py"
echo "3. API will be available at http://localhost:8000"
echo "4. API docs at http://localhost:8000/docs"
