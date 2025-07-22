# Docker Deployment Helper Script

Write-Host "DOCKER DEPLOYMENT HELPER" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

# Check if Docker is running
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
$dockerVersion = docker --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Docker is running: $dockerVersion" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit
}

# Check if image exists
Write-Host "`nChecking for shipping-gui image..." -ForegroundColor Yellow
$imageExists = docker images shipping-gui --format "{{.Repository}}" 2>$null
if ($imageExists) {
    Write-Host "[OK] Image 'shipping-gui' found" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Image 'shipping-gui' not found. Build it first." -ForegroundColor Red
    exit
}

# Docker Hub deployment
Write-Host "`nDOCKER HUB DEPLOYMENT" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host "`nTo deploy your app, we'll push it to Docker Hub first." -ForegroundColor Yellow

# Check if logged in to Docker Hub
Write-Host "`nChecking Docker Hub login..." -ForegroundColor Yellow
$whoami = docker info 2>&1 | Select-String "Username"
if ($whoami) {
    Write-Host "[OK] Already logged in to Docker Hub" -ForegroundColor Green
} else {
    Write-Host "[!] Not logged in to Docker Hub" -ForegroundColor Yellow
    Write-Host "`nDo you have a Docker Hub account? (Y/N)" -ForegroundColor Cyan
    $hasAccount = Read-Host
    
    if ($hasAccount -ne 'Y' -and $hasAccount -ne 'y') {
        Write-Host "`nCreate a free account at: https://hub.docker.com/signup" -ForegroundColor Yellow
        Start-Process "https://hub.docker.com/signup"
        Write-Host "Press Enter after creating your account..." -ForegroundColor Green
        Read-Host
    }
    
    Write-Host "`nLogging in to Docker Hub..." -ForegroundColor Yellow
    docker login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Login failed" -ForegroundColor Red
        exit
    }
}

# Get Docker Hub username
Write-Host "`nEnter your Docker Hub username:" -ForegroundColor Yellow
$dockerUsername = Read-Host

if (-not $dockerUsername) {
    Write-Host "[ERROR] Username is required" -ForegroundColor Red
    exit
}

# Tag the image
$taggedImage = "$dockerUsername/shipping-gui:latest"
Write-Host "`nTagging image as: $taggedImage" -ForegroundColor Yellow
docker tag shipping-gui $taggedImage

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Image tagged successfully" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to tag image" -ForegroundColor Red
    exit
}

# Push to Docker Hub
Write-Host "`nPushing image to Docker Hub..." -ForegroundColor Yellow
Write-Host "This may take a few minutes depending on your internet speed." -ForegroundColor Gray
docker push $taggedImage

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ SUCCESS! Image pushed to Docker Hub" -ForegroundColor Green
    Write-Host "Your image is now available at:" -ForegroundColor Cyan
    Write-Host "docker.io/$taggedImage" -ForegroundColor White
    
    # Deployment options
    Write-Host "`nDEPLOYMENT OPTIONS:" -ForegroundColor Cyan
    Write-Host "===================" -ForegroundColor Cyan
    
    Write-Host "`n1. Google Cloud Run (FREE tier)" -ForegroundColor Green
    Write-Host "   - Visit: https://console.cloud.google.com/run" -ForegroundColor White
    Write-Host "   - Use image: docker.io/$taggedImage" -ForegroundColor White
    
    Write-Host "`n2. Railway" -ForegroundColor Blue
    Write-Host "   - Visit: https://railway.app" -ForegroundColor White
    Write-Host "   - Deploy Docker Image: docker.io/$taggedImage" -ForegroundColor White
    
    Write-Host "`n3. Render.com (FREE tier)" -ForegroundColor Magenta
    Write-Host "   - Visit: https://render.com" -ForegroundColor White
    Write-Host "   - New Web Service from Docker" -ForegroundColor White
    
    Write-Host "`n4. DigitalOcean App Platform" -ForegroundColor Cyan
    Write-Host "   - Visit: https://cloud.digitalocean.com/apps" -ForegroundColor White
    
    Write-Host "`nWhich platform would you like to deploy to? (1-4)" -ForegroundColor Yellow
    $choice = Read-Host
    
    switch ($choice) {
        1 { Start-Process "https://console.cloud.google.com/run" }
        2 { Start-Process "https://railway.app" }
        3 { Start-Process "https://render.com" }
        4 { Start-Process "https://cloud.digitalocean.com/apps" }
    }
    
    Write-Host "`nENVIRONMENT VARIABLES TO ADD:" -ForegroundColor Yellow
    Write-Host "VEEQO_API_KEY=Vqt/7a55360df188537a330a977ef0034942" -ForegroundColor Gray
    Write-Host "EASYSHIP_API_KEY=prod_VC6QKi48mtqwXpXJubfmT/MsOmzTIG0Qyd89/X61ylc=" -ForegroundColor Gray
    Write-Host "SECRET_KEY=unified_order_system_2025_production_secret_key_v2" -ForegroundColor Gray
    
} else {
    Write-Host "[ERROR] Failed to push image" -ForegroundColor Red
}
