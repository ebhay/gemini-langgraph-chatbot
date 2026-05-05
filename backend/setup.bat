@echo off
echo === Gemini LangGraph Chatbot Backend Setup ===
echo.

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo WARNING: Edit .env file and add your credentials:
    echo    - GEMINI_API_KEY
    echo    - JWT_SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_hex(32))")
    echo    - SMTP_USER (your Gmail address)
    echo    - SMTP_PASSWORD (Gmail app password)
    echo    - SMTP_FROM_EMAIL (your Gmail address)
    echo.
)

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your credentials
echo 2. Run: python run.py
echo 3. API will be available at http://localhost:8000
echo 4. API docs at http://localhost:8000/docs

pause
