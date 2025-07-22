# Deployment Helper for Unified Order Management System

Write-Host "`nDEPLOYMENT HELPER" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

# Check Git status
Write-Host "`nChecking Git status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Git not initialized. Initializing now..." -ForegroundColor Red
    git init
    git add .
    git commit -m "Initial commit - Production ready Flask app"
    Write-Host "[OK] Git repository initialized!" -ForegroundColor Green
} else {
    if ($gitStatus) {
        Write-Host "[!] You have uncommitted changes:" -ForegroundColor Yellow
        git status --short
        Write-Host "`nCommit these changes before deployment!" -ForegroundColor Yellow
    } else {
        Write-Host "[OK] Git repository is clean and ready!" -ForegroundColor Green
    }
}

Write-Host "`nDEPLOYMENT OPTIONS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "[1] RAILWAY (Recommended - Easy and Modern)" -ForegroundColor Green
Write-Host "    - Visit: https://railway.app" -ForegroundColor White
Write-Host "    - Click 'New Project' then 'Deploy from GitHub repo'" -ForegroundColor White
Write-Host "    - Connect this repository" -ForegroundColor White
Write-Host "    - Add these environment variables:" -ForegroundColor White
Write-Host "      * VEEQO_API_KEY" -ForegroundColor Yellow
Write-Host "      * EASYSHIP_API_KEY" -ForegroundColor Yellow
Write-Host "      * SECRET_KEY" -ForegroundColor Yellow
Write-Host ""

Write-Host "[2] HEROKU (Traditional PaaS)" -ForegroundColor Blue
Write-Host "    Commands to run:" -ForegroundColor White
Write-Host "    heroku create your-app-name" -ForegroundColor Gray
Write-Host "    heroku config:set VEEQO_API_KEY=your_key" -ForegroundColor Gray
Write-Host "    heroku config:set EASYSHIP_API_KEY=your_key" -ForegroundColor Gray
Write-Host "    heroku config:set SECRET_KEY=your_secret" -ForegroundColor Gray
Write-Host "    git push heroku main" -ForegroundColor Gray
Write-Host ""

Write-Host "[3] DOCKER (For any cloud provider)" -ForegroundColor Magenta
Write-Host "    Build command:" -ForegroundColor White
Write-Host "    docker build -t shipping-gui ." -ForegroundColor Gray
Write-Host "    docker run -p 5000:5000 --env-file .env shipping-gui" -ForegroundColor Gray
Write-Host ""

Write-Host "IMPORTANT NOTES:" -ForegroundColor Yellow
Write-Host "- Ensure requirements.txt is up to date" -ForegroundColor White
Write-Host "- Set all required environment variables" -ForegroundColor White
Write-Host "- The app uses Gunicorn for production (see Procfile)" -ForegroundColor White
Write-Host "- Default port is 5000 (configurable via PORT env var)" -ForegroundColor White

Write-Host "`n[OK] Ready to deploy! Choose your platform above." -ForegroundColor Green
