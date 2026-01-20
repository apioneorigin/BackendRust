$body = @{
    evidence = @(
        @{
            name = "Consciousness"
            value = 0.8
            confidence = 0.9
        }
    )
    targets = @("Maya", "Karma")
} | ConvertTo-Json -Depth 3

Write-Host "Sending request to inference service..."
$response = Invoke-RestMethod -Uri "http://localhost:8080/infer" -Method Post -Body $body -ContentType "application/json"

Write-Host "`nResponse:"
$response | ConvertTo-Json -Depth 10