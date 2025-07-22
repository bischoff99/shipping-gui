# GitHub Setup Script

Write-Host "`nGITHUB SETUP HELPER" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan

Write-Host "`nThis script will help you push your code to GitHub." -ForegroundColor Yellow
Write-Host "Make sure you have created a repository on GitHub first!" -ForegroundColor Yellow

Write-Host "`nStep 1: Create a repository on GitHub" -ForegroundColor Green
Write-Host "- Go to: https://github.com/new" -ForegroundColor White
Write-Host "- Name it 'shipping-gui' or similar" -ForegroundColor White
Write-Host "- DON'T initialize with README" -ForegroundColor Red
Write-Host "- Click 'Create repository'" -ForegroundColor White

Write-Host "`nHave you created the GitHub repository? (Y/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "`nEnter your GitHub username:" -ForegroundColor Yellow
    $username = Read-Host
    
    Write-Host "Enter your repository name (e.g., shipping-gui):" -ForegroundColor Yellow
    $reponame = Read-Host
    
    $repoUrl = "https://github.com/$username/$reponame.git"
    
    Write-Host "`nSetting up remote repository: $repoUrl" -ForegroundColor Green
    
    # Add remote
    git remote add origin $repoUrl
    
    # Rename branch to main
    git branch -M main
    
    Write-Host "`nPushing code to GitHub..." -ForegroundColor Green
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ SUCCESS! Your code is now on GitHub!" -ForegroundColor Green
        Write-Host "`nNext steps:" -ForegroundColor Yellow
        Write-Host "1. Go to https://railway.app" -ForegroundColor White
        Write-Host "2. Sign in with GitHub" -ForegroundColor White
        Write-Host "3. Deploy your repository!" -ForegroundColor White
        
        # Open Railway in browser
        Write-Host "`nWould you like to open Railway.app now? (Y/N)" -ForegroundColor Yellow
        $openRailway = Read-Host
        if ($openRailway -eq 'Y' -or $openRailway -eq 'y') {
            Start-Process "https://railway.app"
        }
    } else {
        Write-Host "`n❌ Push failed. Common issues:" -ForegroundColor Red
        Write-Host "- Make sure you created the repository on GitHub" -ForegroundColor Yellow
        Write-Host "- Check your GitHub username and repository name" -ForegroundColor Yellow
        Write-Host "- You may need to authenticate with GitHub" -ForegroundColor Yellow
    }
} else {
    Write-Host "`nPlease create a GitHub repository first, then run this script again." -ForegroundColor Yellow
    Write-Host "Opening GitHub in your browser..." -ForegroundColor Green
    Start-Process "https://github.com/new"
}
