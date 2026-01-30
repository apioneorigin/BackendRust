@echo off
title Reality Transformer - Launcher
cd /d "%~dp0"

set BACKEND_PORT=8000
set FRONTEND_PORT=5173

echo Closing existing windows...
taskkill /F /FI "WINDOWTITLE eq RT-Backend" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq RT-Frontend" >nul 2>&1
timeout /t 1 >nul

echo Starting services...
start "RT-Backend" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port %BACKEND_PORT%"
start "RT-Frontend" cmd /k "cd frontend-svelte && npm run dev -- --host 0.0.0.0 --port %FRONTEND_PORT%"

echo.
echo Frontend: http://localhost:%FRONTEND_PORT%
echo Backend:  http://localhost:%BACKEND_PORT%
