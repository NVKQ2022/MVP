@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo Support Screenshot Chatbot - Quick Start Runner
echo ============================================================

cd /d "%~dp0"

:: 1. Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.10+ from python.org and add to PATH.
    pause
    exit /b 1
)

:: 2. Check or create virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment in .\venv...
    python -m venv venv
    echo Installing dependencies from requirements.txt...
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\python.exe -m pip install -r requirements.txt
)

:: 3. Check .env configuration
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env from .env.example...
        copy .env.example .env >nul
    )
)

:: 4. Start Application Server
echo.
echo Starting ChatbotOCR Web Application...
echo Web Chat UI:        http://localhost:8000
echo Swagger API Docs:   http://localhost:8000/docs
echo ============================================================
venv\Scripts\python.exe main.py server --host 0.0.0.0 --port 8000
pause
