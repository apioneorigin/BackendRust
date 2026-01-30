@echo off
REM ============================================
REM BackendRust Development Server Startup Script
REM ============================================
REM
REM Starts:
REM - Python/FastAPI backend on port 8000
REM - SvelteKit frontend on port 5173 (unified 4-box layout with embedded matrix)
REM
REM Features:
REM - Kills all existing servers and old cmd windows
REM - Starts fresh instances in new windows
REM

cd /d "%~dp0"

set BACKEND_PORT=8000
set FRONTEND_PORT=5173

echo ============================================
echo   BackendRust Development Server
echo ============================================
echo.

REM Kill existing processes on ports
echo [1/4] Stopping existing services on ports...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill old cmd windows with our servers
echo [2/4] Cleaning up old windows...
taskkill /FI "WINDOWTITLE eq Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Backend API*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend SvelteKit*" /F >nul 2>&1

REM Kill any orphaned processes
taskkill /F /IM "uvicorn.exe" >nul 2>&1
for /f "tokens=2" %%a in ('tasklist ^| findstr /i "node.exe"') do (
    wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /i "vite" >nul && taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 >nul

echo [3/4] Starting backend server...
start "Backend API" cmd /k "cd backend && call venv\Scripts\activate && echo Starting Backend API... && python -m uvicorn main:app --host 0.0.0.0 --port %BACKEND_PORT% --reload"

timeout /t 2 >nul

echo [4/4] Starting frontend server...
start "Frontend SvelteKit" cmd /k "cd frontend-svelte && echo Starting SvelteKit Frontend... && npm run dev -- --host 0.0.0.0 --port %FRONTEND_PORT%"

echo.
echo ============================================
echo   Services Starting...
echo ============================================
echo.
echo   Frontend: http://localhost:%FRONTEND_PORT%
echo   Backend:  http://localhost:%BACKEND_PORT%
echo   API Docs: http://localhost:%BACKEND_PORT%/docs
echo.
echo   Layout: Unified 4-box with embedded matrix
echo   - Sidebar: Conversation history
echo   - Chat: Response container + Input panel
echo   - Matrix: 5x5 transformation grid
echo   - Preview: Live coherence metrics
echo.
echo ============================================
