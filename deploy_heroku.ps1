# Heroku Deployment Script for Shipping GUI

Write-Host "`nHEROKU DEPLOYMENT GUIDE" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan

# Check if Heroku CLI is installed
Write-Host "`nChecking Heroku CLI..." -ForegroundColor Yellow
$herokuInstalled = $false
try {
    $herokuVersion = heroku --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Heroku CLI is installed: $herokuVersion" -ForegroundColor Green
        $herokuInstalled = $true
    }
} catch {
    $herokuInstalled = $false
}

if (-not $herokuInstalled) {
    Write-Host "[X] Heroku CLI not found!" -ForegroundColor Red
    Write-Host "`nTo install Heroku CLI:" -ForegroundColor Yellow
    Write-Host "1. Visit: https://devcenter.heroku.com/articles/heroku-cli" -ForegroundColor White
    Write-Host "2. Download the Windows installer" -ForegroundColor White
    Write-Host "3. Run the installer and restart PowerShell" -ForegroundColor White
    Write-Host "4. Run this script again" -ForegroundColor White
    exit
}

# Deployment steps
Write-Host "`nSTEP-BY-STEP HEROKU DEPLOYMENT:" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green

Write-Host "`n1. Login to Heroku:" -ForegroundColor Yellow
Write-Host "   heroku login" -ForegroundColor Gray

Write-Host "`n2. Create a new Heroku app (choose a unique name):" -ForegroundColor Yellow
Write-Host "   heroku create your-unique-app-name" -ForegroundColor Gray

Write-Host "`n3. Set environment variables:" -ForegroundColor Yellow
Write-Host "   heroku config:set VEEQO_API_KEY=your_veeqo_api_key" -ForegroundColor Gray
Write-Host "   heroku config:set EASYSHIP_API_KEY=your_easyship_api_key" -ForegroundColor Gray
Write-Host "   heroku config:set SECRET_KEY=your_secret_key_here" -ForegroundColor Gray

Write-Host "`n4. Add Heroku remote (if not automatically added):" -ForegroundColor Yellow
Write-Host "   heroku git:remote -a your-app-name" -ForegroundColor Gray

Write-Host "`n5. Deploy your app:" -ForegroundColor Yellow
Write-Host "   git push heroku master" -ForegroundColor Gray

Write-Host "`n6. Open your deployed app:" -ForegroundColor Yellow
Write-Host "   heroku open" -ForegroundColor Gray

Write-Host "`nUSEFUL HEROKU COMMANDS:" -ForegroundColor Cyan
Write-Host "- View logs: heroku logs --tail" -ForegroundColor White
Write-Host "- Restart app: heroku restart" -ForegroundColor White
Write-Host "- Check app info: heroku info" -ForegroundColor White
Write-Host "- Scale dynos: heroku ps:scale web=1" -ForegroundColor White

Write-Host "`nWould you like to start the deployment process? (Y/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "`nStarting Heroku login..." -ForegroundColor Green
    heroku login
    
    Write-Host "`nEnter a unique name for your Heroku app:" -ForegroundColor Yellow
    $appName = Read-Host
    
    Write-Host "`nCreating Heroku app: $appName" -ForegroundColor Green
    heroku create $appName
    
    Write-Host "`nNow you need to set your environment variables." -ForegroundColor Yellow
    Write-Host "Run these commands with your actual API keys:" -ForegroundColor Yellow
    Write-Host "heroku config:set VEEQO_API_KEY=your_key" -ForegroundColor Gray
    Write-Host "heroku config:set EASYSHIP_API_KEY=your_key" -ForegroundColor Gray
    Write-Host "heroku config:set SECRET_KEY=your_secret" -ForegroundColor Gray
}
