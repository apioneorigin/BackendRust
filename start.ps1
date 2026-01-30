$Host.UI.RawUI.WindowTitle = "Reality Transformer - Launcher"
Set-Location $PSScriptRoot

$BACKEND_PORT = 8000
$FRONTEND_PORT = 5173

Write-Host "Closing existing windows..."
Get-Process cmd -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -match "^RT-(Backend|Frontend)" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

Write-Host "Starting services..."
Start-Process cmd -ArgumentList "/k title RT-Backend && cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT"
Start-Process cmd -ArgumentList "/k title RT-Frontend && cd frontend-svelte && npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT"

Write-Host ""
Write-Host "Frontend: http://localhost:$FRONTEND_PORT"
Write-Host "Backend:  http://localhost:$BACKEND_PORT"
