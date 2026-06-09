Write-Host "Starting Registry service on port 10000..."
$registry = Start-Process -FilePath "uv" -ArgumentList "run", "python", "-m", "registry" -PassThru
Start-Sleep -Seconds 2

Write-Host "Starting Tax Agent on port 10102..."
$tax = Start-Process -FilePath "uv" -ArgumentList "run", "python", "-m", "tax_agent" -PassThru

Write-Host "Starting Compliance Agent on port 10103..."
$compliance = Start-Process -FilePath "uv" -ArgumentList "run", "python", "-m", "compliance_agent" -PassThru
Start-Sleep -Seconds 3

Write-Host "Starting Law Agent on port 10101..."
$law = Start-Process -FilePath "uv" -ArgumentList "run", "python", "-m", "law_agent" -PassThru
Start-Sleep -Seconds 3

Write-Host "Starting Customer Agent on port 10100..."
$customer = Start-Process -FilePath "uv" -ArgumentList "run", "python", "-m", "customer_agent" -PassThru

Write-Host "All services started."
Write-Host "Press Ctrl+C to stop all services."

# Keep the script running to prevent background processes from being cleaned up
try {
    Wait-Process -Id $registry.Id, $tax.Id, $compliance.Id, $law.Id, $customer.Id
} catch {
    Write-Host "Error waiting for processes, entering sleep loop..."
    while ($true) {
        Start-Sleep -Seconds 2
    }
}
