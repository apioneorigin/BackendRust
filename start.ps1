# Reality Transformer - Windows PowerShell Startup Script

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "           Reality Transformer - Startup Script" -ForegroundColor Cyan
Write-Host "      Consciousness-Based Transformation Engine" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory and change to it
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Check if backend directory exists
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: backend directory not found!" -ForegroundColor Red
    exit 1
}

Set-Location backend

# Check for Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Dependencies installed" -ForegroundColor Green

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "WARNING: No .env file found!" -ForegroundColor Yellow
    Write-Host "To enable OpenAI features:" -ForegroundColor Yellow
    Write-Host "  1. Copy .env.example to .env" -ForegroundColor Yellow
    Write-Host "  2. Add your OpenAI API key" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Running in fallback mode without OpenAI..." -ForegroundColor Yellow
} else {
    Write-Host "[OK] .env file found" -ForegroundColor Green
}

# Start the server
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Starting Reality Transformer on http://localhost:3000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

python -m uvicorn main:app --host 0.0.0.0 --port 3000
