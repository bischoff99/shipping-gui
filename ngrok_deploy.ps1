Write-Host "NGROK DEPLOYMENT HELPER" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will expose your local Flask app to the internet using ngrok" -ForegroundColor Yellow
Write-Host ""

# Check if Flask app is running
$flaskRunning = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
if (-not $flaskRunning) {
    Write-Host "[WARNING] Flask app doesn't seem to be running on port 5000" -ForegroundColor Yellow
    Write-Host "Make sure your Flask app is running first!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To start your Flask app, run in another terminal:" -ForegroundColor Cyan
    Write-Host "python app.py" -ForegroundColor Green
    Write-Host ""
    $continue = Read-Host "Do you want to continue anyway? (Y/N)"
    if ($continue -ne "Y") {
        exit
    }
}

# Check for ngrok
$ngrokPath = $null

# Check common locations
$possiblePaths = @(
    ".\ngrok.exe",
    "$env:USERPROFILE\Downloads\ngrok.exe",
    "$env:USERPROFILE\Desktop\ngrok.exe",
    "C:\ngrok\ngrok.exe",
    "$env:ProgramFiles\ngrok\ngrok.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $ngrokPath = $path
        break
    }
}

if (-not $ngrokPath) {
    Write-Host "[ERROR] ngrok not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please specify the path to ngrok.exe:" -ForegroundColor Yellow
    $ngrokPath = Read-Host "Enter full path to ngrok.exe"
    
    if (-not (Test-Path $ngrokPath)) {
        Write-Host "[ERROR] ngrok.exe not found at: $ngrokPath" -ForegroundColor Red
        Write-Host ""
        Write-Host "To get ngrok:" -ForegroundColor Cyan
        Write-Host "1. Go to: https://ngrok.com/download" -ForegroundColor Yellow
        Write-Host "2. Download for Windows" -ForegroundColor Yellow
        Write-Host "3. Extract and run this script again" -ForegroundColor Yellow
        exit
    }
}

Write-Host "[OK] Found ngrok at: $ngrokPath" -ForegroundColor Green
Write-Host ""

# Check if user has ngrok account
Write-Host "Do you have an ngrok account? (Recommended for stable URLs)" -ForegroundColor Cyan
$hasAccount = Read-Host "Y/N"

if ($hasAccount -eq "Y") {
    Write-Host ""
    Write-Host "If you haven't added your authtoken yet, get it from:" -ForegroundColor Yellow
    Write-Host "https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Add authtoken? (Y/N)" -ForegroundColor Yellow
    $addToken = Read-Host
    
    if ($addToken -eq "Y") {
        $authToken = Read-Host "Enter your ngrok authtoken" -AsSecureString
        $authTokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($authToken))
        
        Write-Host "Adding authtoken..." -ForegroundColor Yellow
        & $ngrokPath config add-authtoken $authTokenPlain
        Write-Host "[OK] Authtoken added" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Starting ngrok tunnel..." -ForegroundColor Cyan
Write-Host "This will expose your Flask app at port 5000 to the internet" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the tunnel" -ForegroundColor Red
Write-Host ""

# Start ngrok
& $ngrokPath http 5000

# After ngrok is closed
Write-Host ""
Write-Host "Tunnel closed." -ForegroundColor Yellow
