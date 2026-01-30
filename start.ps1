# ============================================
# BackendRust Development Server Startup Script
# ============================================
#
# Starts:
# - Python/FastAPI backend on port 8000 (with SQLite for local dev)
# - SvelteKit frontend on port 5173
#
# Features:
# - Auto-creates Python venv if missing
# - Installs dependencies automatically
# - Kills all existing servers and old PowerShell/cmd windows
# - Uses SQLite for local development (no external database needed)
#
# UI Layout:
# - Unified collapsible sidebar (consistent across all pages)
# - Chat page: 4-box layout with matrix and live preview
#

Set-Location $PSScriptRoot

$BACKEND_PORT = 8000
$FRONTEND_PORT = 5173
$CurrentPID = $PID

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  BackendRust Development Server" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Kill existing processes on ports
Write-Host "[1/5] Stopping existing services on ports..." -ForegroundColor Yellow
foreach ($port in @($BACKEND_PORT, $FRONTEND_PORT)) {
    try {
        Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty OwningProcess -Unique |
            Where-Object { $_ -ne $CurrentPID } |
            ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
    } catch { }
}

# Kill old windows running our servers
Write-Host "[2/5] Cleaning up old windows..." -ForegroundColor Yellow

# Kill processes by name pattern
Get-Process -Name "python" -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowTitle -like "*Backend*" } |
    Stop-Process -Force -ErrorAction SilentlyContinue

Get-Process -Name "node" -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowTitle -like "*Frontend*" } |
    Stop-Process -Force -ErrorAction SilentlyContinue

# Kill cmd/powershell windows with our titles
Get-Process -Name "cmd", "powershell", "pwsh" -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowTitle -like "*Backend*" -or $_.MainWindowTitle -like "*Frontend*" } |
    Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 1

# Check and setup backend venv
Write-Host "[3/5] Checking backend environment..." -ForegroundColor Yellow
if (-not (Test-Path "backend\venv")) {
    Write-Host "    Creating Python virtual environment..." -ForegroundColor White
    Set-Location backend
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create venv. Make sure Python is installed." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "    Installing dependencies..." -ForegroundColor White
    & .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Set-Location ..
    Write-Host "    Backend environment ready!" -ForegroundColor Green
} else {
    Write-Host "    Backend venv found." -ForegroundColor Gray
}

# Check frontend node_modules
Write-Host "[4/5] Checking frontend environment..." -ForegroundColor Yellow
if (-not (Test-Path "frontend-svelte\node_modules")) {
    Write-Host "    Installing npm dependencies..." -ForegroundColor White
    Set-Location frontend-svelte
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install npm dependencies." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Set-Location ..
    Write-Host "    Frontend dependencies ready!" -ForegroundColor Green
} else {
    Write-Host "    Frontend node_modules found." -ForegroundColor Gray
}

Start-Sleep -Seconds 1

Write-Host "[5/5] Starting servers..." -ForegroundColor Yellow

# Start backend with USE_SQLITE for local dev
$backendCmd = @"
Set-Location '$PSScriptRoot\backend'
`$env:USE_SQLITE = 'true'
.\venv\Scripts\Activate.ps1
Write-Host ''
Write-Host '========================================' -ForegroundColor Green
Write-Host '  Backend API starting on port $BACKEND_PORT' -ForegroundColor Green
Write-Host '  Database: SQLite (local development)' -ForegroundColor Gray
Write-Host '========================================' -ForegroundColor Green
Write-Host ''
python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

Start-Sleep -Seconds 3

# Start frontend
$frontendCmd = @"
Set-Location '$PSScriptRoot\frontend-svelte'
Write-Host ''
Write-Host '========================================' -ForegroundColor Green
Write-Host '  Frontend starting on port $FRONTEND_PORT' -ForegroundColor Green
Write-Host '========================================' -ForegroundColor Green
Write-Host ''
npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Services Starting..." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend: " -NoNewline; Write-Host "http://localhost:$FRONTEND_PORT" -ForegroundColor Cyan
Write-Host "  Backend:  " -NoNewline; Write-Host "http://localhost:$BACKEND_PORT" -ForegroundColor Cyan
Write-Host "  API Docs: " -NoNewline; Write-Host "http://localhost:$BACKEND_PORT/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Database: " -NoNewline; Write-Host "SQLite (backend/data/dev.db)" -ForegroundColor Gray
Write-Host ""
Write-Host "  UI Layout:" -ForegroundColor White
Write-Host "  - Collapsible sidebar (all pages)" -ForegroundColor Gray
Write-Host "  - Chat: 4-box grid with matrix" -ForegroundColor Gray
Write-Host "  - Documents, Settings: Content area" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
