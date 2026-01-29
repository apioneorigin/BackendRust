@echo off
REM Reality Transformer - Windows Startup Script
REM Starts Python backend + SvelteKit frontend

echo.
echo ============================================================
echo           Reality Transformer - Startup Script
echo      Consciousness-Based Transformation Engine
echo ============================================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

set BACKEND_PORT=8000
set FRONTEND_PORT=5173

REM Kill existing processes on ports
echo Stopping existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
    echo   Killing process on port %BACKEND_PORT% (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do (
    echo   Killing process on port %FRONTEND_PORT% (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 >nul
echo [OK] Existing services stopped

REM Check if directories exist
if not exist "backend" (
    echo ERROR: backend directory not found!
    pause
    exit /b 1
)

if not exist "frontend-svelte" (
    echo ERROR: frontend-svelte directory not found!
    pause
    exit /b 1
)

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.10+
    pause
    exit /b 1
)
echo [OK] Python found

REM Check for Node
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 18+
    pause
    exit /b 1
)
echo [OK] Node.js found

REM Install Python dependencies
echo.
echo Installing Python dependencies...
cd backend
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo [OK] Python dependencies installed
cd ..

REM Install Node dependencies
echo.
echo Installing Node dependencies...
cd frontend-svelte
if not exist "node_modules" (
    call npm install
)
echo [OK] Node dependencies installed
cd ..

REM Check for .env file
if not exist "backend\.env" (
    echo.
    echo WARNING: No .env file found!
    echo Copy backend\.env.example to backend\.env and add your OpenAI API key.
    echo Running in fallback mode without OpenAI...
    echo.
)

REM Start services
echo.
echo ============================================================
echo Starting Reality Transformer
echo   Frontend: http://localhost:%FRONTEND_PORT%
echo   Backend:  http://localhost:%BACKEND_PORT%
echo Press Ctrl+C to stop
echo ============================================================
echo.

REM Start backend in new window
start "Reality Transformer - Backend" cmd /c "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port %BACKEND_PORT%"

REM Start frontend in new window
start "Reality Transformer - Frontend" cmd /c "cd frontend-svelte && npm run dev -- --host 0.0.0.0 --port %FRONTEND_PORT%"

echo Services started in separate windows.
echo Close this window or press any key to exit (services will keep running).
pause >nul
