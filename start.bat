@echo off
cd /d "%~dp0"

set BACKEND_PORT=8000
set FRONTEND_PORT=5173

echo Stopping existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
timeout /t 1 >nul

echo Starting services...
start "Backend" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port %BACKEND_PORT%"
start "Frontend" cmd /k "cd frontend-svelte && npm run dev -- --host 0.0.0.0 --port %FRONTEND_PORT%"

echo.
echo Frontend: http://localhost:%FRONTEND_PORT%
echo Backend:  http://localhost:%BACKEND_PORT%
