Write-Host "DOCKER HUB PUSH HELPER" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""

# Check if image exists
$imageExists = docker images -q shipping-gui 2>$null
if (-not $imageExists) {
    Write-Host "[ERROR] Image 'shipping-gui' not found!" -ForegroundColor Red
    Write-Host "Run 'docker build -t shipping-gui .' first" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found local image 'shipping-gui'" -ForegroundColor Green
Write-Host ""

# Get username
$username = Read-Host "Enter your Docker Hub username"

# Tag the image
Write-Host "Tagging image as: ${username}/shipping-gui:latest" -ForegroundColor Yellow
docker tag shipping-gui "${username}/shipping-gui:latest"

Write-Host ""
Write-Host "Now we'll push your image to Docker Hub." -ForegroundColor Cyan
Write-Host "You'll be prompted for your Docker Hub password." -ForegroundColor Yellow
Write-Host ""

# Login and push
Write-Host "Logging in to Docker Hub..." -ForegroundColor Yellow
docker login -u $username

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Login successful! Pushing image..." -ForegroundColor Green
    docker push "${username}/shipping-gui:latest"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "SUCCESS! Your image is now on Docker Hub!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your Docker image URL: https://hub.docker.com/r/${username}/shipping-gui" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "DEPLOY YOUR APP:" -ForegroundColor Yellow
        Write-Host "=================" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Google Cloud Run (Free tier available):" -ForegroundColor Cyan
        Write-Host "   - Visit: https://console.cloud.google.com/run"
        Write-Host "   - Click 'Create Service'"
        Write-Host "   - Enter image: ${username}/shipping-gui:latest"
        Write-Host ""
        Write-Host "2. Railway.app (Easy, no credit card for trial):" -ForegroundColor Cyan
        Write-Host "   - Visit: https://railway.app/new"
        Write-Host "   - Select 'Deploy from Docker Hub'"
        Write-Host "   - Enter: ${username}/shipping-gui"
        Write-Host ""
        Write-Host "3. Render.com (Free tier):" -ForegroundColor Cyan
        Write-Host "   - Visit: https://render.com/deploy"
        Write-Host "   - Select 'Web Service' > 'Deploy an existing image'"
        Write-Host "   - Enter: docker.io/${username}/shipping-gui:latest"
        Write-Host ""
        Write-Host "Remember to set these environment variables on your chosen platform:" -ForegroundColor Yellow
        Write-Host "- VEEQO_API_KEY"
        Write-Host "- EASYSHIP_API_KEY"
        Write-Host "- SECRET_KEY"
    } else {
        Write-Host "[ERROR] Failed to push image" -ForegroundColor Red
    }
} else {
    Write-Host "[ERROR] Docker Hub login failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "If you forgot your password, reset it at:" -ForegroundColor Yellow
    Write-Host "https://hub.docker.com/reset-password" -ForegroundColor Cyan
}
