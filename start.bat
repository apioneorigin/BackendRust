@echo off
REM Reality Transformer - Windows Startup Script

echo.
echo ============================================================
echo           Reality Transformer - Startup Script
echo      Consciousness-Based Transformation Engine
echo ============================================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

REM Check if registry.json exists
if not exist "registry.json" (
    echo ERROR: registry.json not found!
    echo Run formula_compiler.py first.
    pause
    exit /b 1
)
echo [OK] Registry found

REM Check if backend directory exists
if not exist "backend" (
    echo ERROR: backend directory not found!
    pause
    exit /b 1
)

cd backend

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.10+
    pause
    exit /b 1
)
echo [OK] Python found

REM Install dependencies
echo.
echo Installing dependencies...
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Check for .env file
if not exist ".env" (
    echo.
    echo WARNING: No .env file found!
    echo Copy .env.example to .env and add your OpenAI API key.
    echo Running in fallback mode without OpenAI...
    echo.
)

REM Start the server
echo.
echo ============================================================
echo Starting Reality Transformer on http://localhost:3000
echo Press Ctrl+C to stop
echo ============================================================
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 3000
if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Server crashed or failed to start
    echo Check the error messages above
    echo ============================================================
    pause
)
