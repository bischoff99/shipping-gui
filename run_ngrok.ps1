# Ngrok Runner Script for Shipping GUI

Write-Host "NGROK PUBLIC ACCESS SETUP" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Check if Docker container is running
Write-Host "`nChecking Docker container status..." -ForegroundColor Yellow
$containerStatus = docker ps --filter "name=shipping-gui-container" --format "{{.Status}}"

if ($containerStatus -like "Up*") {
    Write-Host "[OK] Docker container is running on port 5001" -ForegroundColor Green
} else {
    Write-Host "[!] Docker container not running. Starting it..." -ForegroundColor Yellow
    docker start shipping-gui-container
    Start-Sleep -Seconds 3
}

Write-Host "`nNGROK SETUP OPTIONS:" -ForegroundColor Cyan
Write-Host "1. I have ngrok installed and configured" -ForegroundColor White
Write-Host "2. I need to download ngrok first" -ForegroundColor White
Write-Host "3. I need help with auth token" -ForegroundColor White

$choice = Read-Host "`nEnter your choice (1-3)"

switch ($choice) {
    1 {
        Write-Host "`nStarting ngrok tunnel..." -ForegroundColor Green
        Write-Host "Enter the path to ngrok.exe (or just 'ngrok' if it's in PATH):" -ForegroundColor Yellow
        $ngrokPath = Read-Host
        
        if ($ngrokPath -eq "") { $ngrokPath = "ngrok" }
        
        Write-Host "`nStarting public tunnel to your shipping GUI..." -ForegroundColor Green
        Write-Host "Press Ctrl+C to stop the tunnel" -ForegroundColor Yellow
        
        & $ngrokPath http 5001
    }
    2 {
        Write-Host "`nOpening ngrok download page..." -ForegroundColor Green
        Start-Process "https://ngrok.com/download"
        
        Write-Host "`nAfter downloading:" -ForegroundColor Yellow
        Write-Host "1. Extract ngrok.exe to a folder (e.g., C:\ngrok)" -ForegroundColor White
        Write-Host "2. Run this script again and choose option 1" -ForegroundColor White
    }
    3 {
        Write-Host "`nTo get your auth token:" -ForegroundColor Yellow
        Write-Host "1. Sign up at: https://ngrok.com/signup" -ForegroundColor White
        Write-Host "2. Get token from: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor White
        Write-Host "3. Configure ngrok:" -ForegroundColor White
        Write-Host "   ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor Gray
        
        Write-Host "`nOpening ngrok signup page..." -ForegroundColor Green
        Start-Process "https://ngrok.com/signup"
    }
}

Write-Host "`nNote: Your shipping GUI will be accessible worldwide through the ngrok URL!" -ForegroundColor Cyan
