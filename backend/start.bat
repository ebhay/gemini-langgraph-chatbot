@echo off
echo Starting Gemini Chatbot Backend...
echo.

cd /d "%~dp0"

if not exist "venv" (
    echo Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Checking environment variables...
python -c "from config import settings; print('✓ GEMINI_API_KEY:', 'SET' if settings.GEMINI_API_KEY else 'NOT SET'); print('✓ JWT_SECRET_KEY:', 'SET' if settings.JWT_SECRET_KEY else 'NOT SET')"

echo.
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop
echo.

python run.py
