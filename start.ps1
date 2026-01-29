# Reality Transformer - Windows PowerShell Startup Script
# Starts Python backend + SvelteKit frontend

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "           Reality Transformer - Startup Script" -ForegroundColor Cyan
Write-Host "      Consciousness-Based Transformation Engine" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory and change to it
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$BACKEND_PORT = 8000
$FRONTEND_PORT = 5173

# Kill existing processes on ports
Write-Host "Stopping existing services..." -ForegroundColor Yellow
foreach ($port in @($BACKEND_PORT, $FRONTEND_PORT)) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($pid in $pids) {
            if ($pid -and $pid -ne 0) {
                Write-Host "  Killing process on port $port (PID: $pid)..." -ForegroundColor Yellow
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            }
        }
    }
}
Start-Sleep -Seconds 1
Write-Host "[OK] Existing services stopped" -ForegroundColor Green

# Check if backend directory exists
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: backend directory not found!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "frontend-svelte")) {
    Write-Host "ERROR: frontend-svelte directory not found!" -ForegroundColor Red
    exit 1
}

# Check for Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Check for Node
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js not found! Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
Set-Location backend
python -m pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python dependencies installed" -ForegroundColor Green
Set-Location ..

# Install Node dependencies
Write-Host ""
Write-Host "Installing Node dependencies..." -ForegroundColor Yellow
Set-Location frontend-svelte
if (-not (Test-Path "node_modules")) {
    npm install
}
Write-Host "[OK] Node dependencies installed" -ForegroundColor Green
Set-Location ..

# Check for .env file
if (-not (Test-Path "backend/.env")) {
    Write-Host ""
    Write-Host "WARNING: No .env file found!" -ForegroundColor Yellow
    Write-Host "To enable OpenAI features:" -ForegroundColor Yellow
    Write-Host "  1. Copy backend/.env.example to backend/.env" -ForegroundColor Yellow
    Write-Host "  2. Add your OpenAI API key" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Running in fallback mode without OpenAI..." -ForegroundColor Yellow
} else {
    Write-Host "[OK] .env file found" -ForegroundColor Green
}

# Start the backend
Write-Host ""
Write-Host "Starting Python Backend on port $BACKEND_PORT..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    param($dir, $port)
    Set-Location $dir
    python -m uvicorn main:app --host 0.0.0.0 --port $port
} -ArgumentList "$scriptDir/backend", $BACKEND_PORT

# Start the frontend
Write-Host "Starting SvelteKit Frontend on port $FRONTEND_PORT..." -ForegroundColor Cyan
$frontendJob = Start-Job -ScriptBlock {
    param($dir, $port)
    Set-Location $dir
    npm run dev -- --host 0.0.0.0 --port $port
} -ArgumentList "$scriptDir/frontend-svelte", $FRONTEND_PORT

# Wait for services to start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "All services started!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend:  http://localhost:$FRONTEND_PORT" -ForegroundColor White
Write-Host "  Backend:   http://localhost:$BACKEND_PORT" -ForegroundColor White
Write-Host "  Health:    http://localhost:$BACKEND_PORT/health" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Keep script running and show logs
try {
    while ($true) {
        Receive-Job -Job $backendJob -ErrorAction SilentlyContinue
        Receive-Job -Job $frontendJob -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host ""
    Write-Host "Stopping services..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job -Job $frontendJob -ErrorAction SilentlyContinue
    Remove-Job -Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job -Job $frontendJob -ErrorAction SilentlyContinue
    Write-Host "Services stopped." -ForegroundColor Green
}
