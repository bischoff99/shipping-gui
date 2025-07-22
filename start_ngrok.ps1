# Ngrok Quick Start Script for Shipping GUI

Write-Host "NGROK TUNNEL STARTER" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan

# Check if Docker container is running
Write-Host "`nChecking your app status..." -ForegroundColor Yellow
$dockerRunning = docker ps --filter "name=shipping-gui-container" --format "{{.Status}}" 2>$null

if ($dockerRunning -like "Up*") {
    Write-Host "[OK] Docker container is running on port 5001" -ForegroundColor Green
} else {
    Write-Host "[!] Starting Docker container..." -ForegroundColor Yellow
    docker start shipping-gui-container 2>$null
    Start-Sleep -Seconds 3
}

# Navigate to ngrok directory
Set-Location "C:\ngrok"

# Check if ngrok is configured
Write-Host "`nChecking ngrok configuration..." -ForegroundColor Yellow
$configExists = Test-Path "$env:USERPROFILE\.ngrok2\ngrok.yml"

if (-not $configExists) {
    Write-Host "[!] Ngrok not configured yet." -ForegroundColor Yellow
    Write-Host "`nYou need an auth token:" -ForegroundColor Cyan
    Write-Host "1. Sign up at: https://ngrok.com/signup (already opened)" -ForegroundColor White
    Write-Host "2. Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor White
    Write-Host "3. Copy the token (looks like: 2abcXYZ123...)" -ForegroundColor White
    
    Write-Host "`nPaste your auth token here:" -ForegroundColor Yellow
    $authToken = Read-Host
    
    if ($authToken) {
        Write-Host "Configuring ngrok..." -ForegroundColor Green
        & ".\ngrok.exe" config add-authtoken $authToken
        Write-Host "[OK] Ngrok configured!" -ForegroundColor Green
    } else {
        Write-Host "[!] No token provided. Exiting." -ForegroundColor Red
        exit
    }
} else {
    Write-Host "[OK] Ngrok is already configured" -ForegroundColor Green
}

# Start the tunnel
Write-Host "`n🚀 STARTING NGROK TUNNEL..." -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan
Write-Host "`nYour app will be accessible worldwide!" -ForegroundColor Green
Write-Host "Look for the 'Forwarding' URL below" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the tunnel" -ForegroundColor Yellow
Write-Host "`nStarting in 3 seconds..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Start ngrok
& ".\ngrok.exe" http 5001
