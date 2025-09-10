@echo off
REM Start script for Smart Meeting Minutes Generator (Windows)

echo Smart Meeting Minutes Generator - Starting Application
echo ==================================================

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Please run setup first:
    echo python setup.py
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found. Some features may not work.
    echo Please create .env file with your HuggingFace token.
)

REM Start the application
echo Starting FastAPI server...
echo Access the application at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
