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
REM - Kills ALL old server windows before starting
REM - Auto-creates Python venv if missing
REM - Installs dependencies automatically
REM

cd /d "%~dp0"

set BACKEND_PORT=8000
set FRONTEND_PORT=5173

echo ============================================
echo   BackendRust Development Server
echo ============================================
echo.

REM ============================================
REM STEP 1: Kill all existing processes
REM ============================================
echo [1/5] Killing old server processes...

REM Kill by port - most reliable method
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
    echo     Killing process on port %BACKEND_PORT% (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do (
    echo     Killing process on port %FRONTEND_PORT% (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill Python processes running uvicorn
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST 2^>nul ^| findstr "PID"') do (
    wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /i "uvicorn" >nul && (
        echo     Killing uvicorn process (PID: %%a)
        taskkill /F /PID %%a >nul 2>&1
    )
)

REM Kill Node processes running vite/npm dev
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq node.exe" /FO LIST 2^>nul ^| findstr "PID"') do (
    wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /i "vite" >nul && (
        echo     Killing vite process (PID: %%a)
        taskkill /F /PID %%a >nul 2>&1
    )
)

REM ============================================
REM STEP 2: Kill old CMD windows by title
REM ============================================
echo [2/5] Closing old terminal windows...

REM Kill cmd windows with specific titles
taskkill /FI "WINDOWTITLE eq Backend API" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Backend API*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend SvelteKit" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend SvelteKit*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Administrator:*Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Administrator:*Frontend*" /F >nul 2>&1

REM Also try generic patterns
taskkill /FI "WINDOWTITLE eq *uvicorn*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq *vite*" /F >nul 2>&1

REM Wait for processes to fully terminate
timeout /t 2 >nul

REM ============================================
REM STEP 3: Setup backend environment
REM ============================================
echo [3/5] Checking backend environment...
if not exist "backend\venv" (
    echo     Creating Python virtual environment...
    cd backend
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create venv. Make sure Python is installed.
        pause
        exit /b 1
    )
    echo     Installing dependencies...
    call venv\Scripts\activate
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies.
        pause
        exit /b 1
    )
    cd ..
    echo     Backend environment ready!
) else (
    echo     Backend venv found.
)

REM ============================================
REM STEP 4: Setup frontend environment
REM ============================================
echo [4/5] Checking frontend environment...
if not exist "frontend-svelte\node_modules" (
    echo     Installing npm dependencies...
    cd frontend-svelte
    npm install
    if errorlevel 1 (
        echo ERROR: Failed to install npm dependencies.
        pause
        exit /b 1
    )
    cd ..
    echo     Frontend dependencies ready!
) else (
    echo     Frontend node_modules found.
)

REM ============================================
REM STEP 5: Start fresh servers
REM ============================================
echo [5/5] Starting fresh server windows...

REM Start backend in new window
start "Backend API" cmd /k "cd /d "%~dp0backend" && call venv\Scripts\activate && echo. && echo ======================================== && echo   Backend API starting on port %BACKEND_PORT% && echo ======================================== && echo. && python -m uvicorn main:app --host 0.0.0.0 --port %BACKEND_PORT% --reload"

REM Wait for backend to initialize
timeout /t 3 >nul

REM Start frontend in new window
start "Frontend SvelteKit" cmd /k "cd /d "%~dp0frontend-svelte" && echo. && echo ======================================== && echo   Frontend starting on port %FRONTEND_PORT% && echo ======================================== && echo. && npm run dev -- --host 0.0.0.0 --port %FRONTEND_PORT%"

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
echo.
echo Press any key to close this window...
pause >nul
