# ============================================
# BackendRust Development Server Startup Script
# ============================================
#
# Starts:
# - Python/FastAPI backend on port 8000
# - SvelteKit frontend on port 5173 (unified 4-box layout with embedded matrix)
#
# Features:
# - Kills all existing servers and old PowerShell/cmd windows
# - Starts fresh instances in new windows
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
Write-Host "[1/4] Stopping existing services on ports..." -ForegroundColor Yellow
foreach ($port in @($BACKEND_PORT, $FRONTEND_PORT)) {
    try {
        Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty OwningProcess -Unique |
            Where-Object { $_ -ne $CurrentPID } |
            ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
    } catch { }
}

# Kill old windows running our servers
Write-Host "[2/4] Cleaning up old windows..." -ForegroundColor Yellow

# Kill processes by name pattern
Get-Process -Name "python" -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowTitle -like "*Backend*" -or $_.CommandLine -like "*uvicorn*" } |
    Stop-Process -Force -ErrorAction SilentlyContinue

Get-Process -Name "node" -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowTitle -like "*Frontend*" -or $_.CommandLine -like "*vite*" } |
    Stop-Process -Force -ErrorAction SilentlyContinue

# Kill cmd windows with our titles
Get-Process -Name "cmd" -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowTitle -like "*Backend*" -or $_.MainWindowTitle -like "*Frontend*" } |
    Stop-Process -Force -ErrorAction SilentlyContinue

# Kill any uvicorn processes
Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

Write-Host "[3/4] Starting backend server..." -ForegroundColor Yellow
$backendCmd = "cd backend; .\venv\Scripts\Activate.ps1; Write-Host 'Starting Backend API...' -ForegroundColor Green; python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

Start-Sleep -Seconds 2

Write-Host "[4/4] Starting frontend server..." -ForegroundColor Yellow
$frontendCmd = "cd frontend-svelte; Write-Host 'Starting SvelteKit Frontend...' -ForegroundColor Green; npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT"
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
Write-Host "  Layout: Unified 4-box with embedded matrix" -ForegroundColor White
Write-Host "  - Sidebar: Conversation history" -ForegroundColor Gray
Write-Host "  - Chat: Response container + Input panel" -ForegroundColor Gray
Write-Host "  - Matrix: 5x5 transformation grid" -ForegroundColor Gray
Write-Host "  - Preview: Live coherence metrics" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
