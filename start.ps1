Set-Location $PSScriptRoot

$BACKEND_PORT = 8000
$FRONTEND_PORT = 5173

Write-Host "Stopping existing services..."
foreach ($port in @($BACKEND_PORT, $FRONTEND_PORT)) {
    Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
}
Start-Sleep -Seconds 1

Write-Host "Starting services..."
Start-Process cmd -ArgumentList "/k cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT"
Start-Process cmd -ArgumentList "/k cd frontend-svelte && npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT"

Write-Host ""
Write-Host "Frontend: http://localhost:$FRONTEND_PORT"
Write-Host "Backend:  http://localhost:$BACKEND_PORT"
