# Ngrok Download Script for Windows

Write-Host "NGROK DOWNLOADER" -ForegroundColor Cyan
Write-Host "================" -ForegroundColor Cyan

# Create ngrok directory if it doesn't exist
$ngrokDir = "C:\ngrok"
if (!(Test-Path $ngrokDir)) {
    Write-Host "Creating directory: $ngrokDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $ngrokDir -Force | Out-Null
}

# Download URL for Windows 64-bit
$downloadUrl = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
$zipPath = "$ngrokDir\ngrok.zip"
$extractPath = $ngrokDir

Write-Host "`nDownloading ngrok..." -ForegroundColor Green
Write-Host "From: $downloadUrl" -ForegroundColor Gray
Write-Host "To: $zipPath" -ForegroundColor Gray

try {
    # Download the file
    Write-Host "`nDownloading... Please wait..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing
    
    Write-Host "[OK] Download complete!" -ForegroundColor Green
    
    # Extract the zip file
    Write-Host "`nExtracting ngrok..." -ForegroundColor Yellow
    Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
    
    Write-Host "[OK] Extraction complete!" -ForegroundColor Green
    
    # Clean up zip file
    Remove-Item $zipPath -Force
    
    Write-Host "`n✅ NGROK INSTALLED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "Location: $ngrokDir\ngrok.exe" -ForegroundColor White
    
    # Next steps
    Write-Host "`nNEXT STEPS:" -ForegroundColor Cyan
    Write-Host "1. Sign up at: https://ngrok.com/signup" -ForegroundColor White
    Write-Host "2. Get your auth token from dashboard" -ForegroundColor White
    Write-Host "3. Configure ngrok with:" -ForegroundColor White
    Write-Host "   cd $ngrokDir" -ForegroundColor Gray
    Write-Host "   .\ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor Gray
    Write-Host "4. Start tunnel with:" -ForegroundColor White
    Write-Host "   .\ngrok http 5001" -ForegroundColor Gray
    
    # Offer to open signup page
    Write-Host "`nWould you like to open the ngrok signup page now? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        Start-Process "https://ngrok.com/signup"
    }
    
    # Offer to start configuration
    Write-Host "`nWould you like to configure ngrok now? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "Enter your ngrok auth token:" -ForegroundColor Yellow
        $authToken = Read-Host
        
        if ($authToken) {
            Set-Location $ngrokDir
            & ".\ngrok.exe" config add-authtoken $authToken
            Write-Host "[OK] Auth token configured!" -ForegroundColor Green
            
            Write-Host "`nReady to start tunnel? (Y/N)" -ForegroundColor Yellow
            $response = Read-Host
            if ($response -eq 'Y' -or $response -eq 'y') {
                Write-Host "`nStarting ngrok tunnel on port 5001..." -ForegroundColor Green
                Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
                & ".\ngrok.exe" http 5001
            }
        }
    }
    
} catch {
    Write-Host "[ERROR] Failed to download ngrok: $_" -ForegroundColor Red
    Write-Host "`nAlternative: Download manually from https://ngrok.com/download" -ForegroundColor Yellow
}
