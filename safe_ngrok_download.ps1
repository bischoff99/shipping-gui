# Safe Ngrok Download Script
# This script helps download ngrok safely

Write-Host "NGROK SAFE DOWNLOAD HELPER" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan

Write-Host "`nThis script will help you download ngrok safely." -ForegroundColor Yellow
Write-Host "Windows Defender may block it - we'll handle that." -ForegroundColor Yellow

# Create directory
$ngrokDir = "C:\ngrok"
if (!(Test-Path $ngrokDir)) {
    Write-Host "`nCreating directory: $ngrokDir" -ForegroundColor Green
    New-Item -ItemType Directory -Path $ngrokDir -Force | Out-Null
}

# Method 1: Try direct download with handling
Write-Host "`nMethod 1: Attempting direct download..." -ForegroundColor Cyan

$url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
$output = "$ngrokDir\ngrok.zip"

try {
    # Use curl.exe which is built into Windows 10/11
    Write-Host "Downloading using curl..." -ForegroundColor Yellow
    $curlPath = "$env:WINDIR\System32\curl.exe"
    
    if (Test-Path $curlPath) {
        & $curlPath -L -o $output $url
        
        if (Test-Path $output) {
            Write-Host "[OK] Download successful!" -ForegroundColor Green
            
            # Try to extract
            Write-Host "Extracting..." -ForegroundColor Yellow
            try {
                # Use tar which is also built into Windows 10/11
                & tar -xf $output -C $ngrokDir
                Write-Host "[OK] Extraction successful!" -ForegroundColor Green
                Remove-Item $output -Force
                
                if (Test-Path "$ngrokDir\ngrok.exe") {
                    Write-Host "`n✅ NGROK SUCCESSFULLY INSTALLED!" -ForegroundColor Green
                    Write-Host "Location: $ngrokDir\ngrok.exe" -ForegroundColor White
                }
            } catch {
                Write-Host "[!] Extraction failed. Please extract manually." -ForegroundColor Yellow
                Write-Host "ZIP file saved at: $output" -ForegroundColor White
            }
        }
    } else {
        Write-Host "[!] curl.exe not found. Trying alternative method..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "[!] Download failed: $_" -ForegroundColor Red
}

# Method 2: Browser download
if (!(Test-Path "$ngrokDir\ngrok.exe")) {
    Write-Host "`nMethod 2: Browser Download" -ForegroundColor Cyan
    Write-Host "Opening download page in your browser..." -ForegroundColor Yellow
    Write-Host "When prompted by Windows Defender:" -ForegroundColor Yellow
    Write-Host "1. Click '...' (three dots)" -ForegroundColor White
    Write-Host "2. Click 'Keep'" -ForegroundColor White
    Write-Host "3. Click 'Show more'" -ForegroundColor White
    Write-Host "4. Click 'Keep anyway'" -ForegroundColor White
    
    Start-Process $url
    
    Write-Host "`nAfter downloading:" -ForegroundColor Yellow
    Write-Host "1. Extract the ZIP to: $ngrokDir" -ForegroundColor White
    Write-Host "2. Make sure ngrok.exe is in that folder" -ForegroundColor White
    
    Write-Host "`nPress Enter when done..." -ForegroundColor Green
    Read-Host
}

# Check if ngrok is now available
if (Test-Path "$ngrokDir\ngrok.exe") {
    Write-Host "`n✅ Ngrok found! Setting it up..." -ForegroundColor Green
    
    # Get auth token
    Write-Host "`nYou need an auth token from ngrok." -ForegroundColor Yellow
    Write-Host "1. Sign up at: https://ngrok.com/signup" -ForegroundColor White
    Write-Host "2. Get token from: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor White
    
    Write-Host "`nOpen ngrok signup page? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        Start-Process "https://ngrok.com/signup"
    }
    
    Write-Host "`nEnter your ngrok auth token (or press Enter to skip):" -ForegroundColor Yellow
    $authToken = Read-Host
    
    if ($authToken) {
        Set-Location $ngrokDir
        & ".\ngrok.exe" config add-authtoken $authToken
        Write-Host "[OK] Auth token configured!" -ForegroundColor Green
        
        Write-Host "`nReady to start ngrok tunnel on port 5001? (Y/N)" -ForegroundColor Yellow
        $response = Read-Host
        if ($response -eq 'Y' -or $response -eq 'y') {
            Write-Host "`nStarting ngrok..." -ForegroundColor Green
            Write-Host "Your public URL will appear below:" -ForegroundColor Yellow
            Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
            & ".\ngrok.exe" http 5001
        }
    } else {
        Write-Host "`nTo use ngrok later:" -ForegroundColor Yellow
        Write-Host "cd $ngrokDir" -ForegroundColor Gray
        Write-Host ".\ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor Gray
        Write-Host ".\ngrok http 5001" -ForegroundColor Gray
    }
} else {
    Write-Host "`n[!] Ngrok not found. Please:" -ForegroundColor Red
    Write-Host "1. Download manually from: https://ngrok.com/download" -ForegroundColor Yellow
    Write-Host "2. Extract to: $ngrokDir" -ForegroundColor Yellow
    Write-Host "3. Run this script again" -ForegroundColor Yellow
}
