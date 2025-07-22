# PowerShell Production Deployment Script

Write-Host "🚀 Unified Order Management - Production Deployment" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "📋 Initializing Git repository..." -ForegroundColor Yellow
    git init
    git add .
    git commit -m "Initial commit - Production ready Flask app"
}

Write-Host ""
Write-Host "🌐 Choose your deployment platform:" -ForegroundColor Green
Write-Host "1. Heroku (Easiest)" -ForegroundColor White
Write-Host "2. Railway (Modern)" -ForegroundColor White
Write-Host "3. DigitalOcean (Scalable)" -ForegroundColor White
Write-Host "4. Docker Build (Any cloud)" -ForegroundColor White
Write-Host "5. AWS (Enterprise)" -ForegroundColor White

$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    1 {
        Write-Host "🚀 Deploying to Heroku..." -ForegroundColor Cyan
        Write-Host "Run these commands:" -ForegroundColor Yellow
        Write-Host "heroku create your-app-name" -ForegroundColor White
        Write-Host "heroku config:set FLASK_SECRET_KEY=your_secret_key_here" -ForegroundColor White
        Write-Host "git push heroku main" -ForegroundColor White
    }
    2 {
        Write-Host "🚀 Railway deployment:" -ForegroundColor Cyan
        Write-Host "1. Visit https://railway.app" -ForegroundColor White
        Write-Host "2. Connect this GitHub repo" -ForegroundColor White
        Write-Host "3. Set environment variables" -ForegroundColor White
        Write-Host "4. Deploy automatically" -ForegroundColor White
    }
    3 {
        Write-Host "🚀 DigitalOcean App Platform:" -ForegroundColor Cyan
        Write-Host "1. Visit https://cloud.digitalocean.com/apps" -ForegroundColor White
        Write-Host "2. Create new app from GitHub" -ForegroundColor White
        Write-Host "3. Use the .do/app.yaml configuration" -ForegroundColor White
    }
    4 {
        Write-Host "🐳 Building Docker image..." -ForegroundColor Cyan
        docker build -t unified-order-system .
        Write-Host "Docker image built! Push to your registry." -ForegroundColor Green
    }
    5 {
        Write-Host "☁️ AWS deployment requires additional setup" -ForegroundColor Yellow
        Write-Host "Consider using AWS Elastic Beanstalk or ECS" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "✅ Deployment files are ready!" -ForegroundColor Green
Write-Host "📁 Check the deployment guides in your project folder" -ForegroundColor Cyan
