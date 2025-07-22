# Quick Deployment Guide

## Prerequisites
- Git is now initialized ✓
- Make sure you have your API keys ready:
  - VEEQO_API_KEY
  - EASYSHIP_API_KEY
  - A SECRET_KEY (any random string for session security)

## Option 1: Deploy to Railway (Easiest - Recommended)

1. **Create a GitHub repository:**
   ```bash
   # First, create a new repo on GitHub.com
   # Then run these commands:
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin master
   ```

2. **Deploy on Railway:**
   - Visit https://railway.app
   - Sign up/Login with GitHub
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect it's a Flask app

3. **Set Environment Variables in Railway:**
   - Go to your project's Variables tab
   - Add these variables:
     ```
     VEEQO_API_KEY=your_veeqo_api_key_here
     EASYSHIP_API_KEY=your_easyship_api_key_here
     SECRET_KEY=any_random_string_for_security
     ```

4. **Done!** Railway will provide you with a URL like `yourapp.railway.app`

## Option 2: Deploy to Heroku

1. **Install Heroku CLI** from https://devcenter.heroku.com/articles/heroku-cli

2. **Login and create app:**
   ```bash
   heroku login
   heroku create your-unique-app-name
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set VEEQO_API_KEY=your_veeqo_api_key_here
   heroku config:set EASYSHIP_API_KEY=your_easyship_api_key_here
   heroku config:set SECRET_KEY=any_random_string_for_security
   ```

4. **Deploy:**
   ```bash
   git push heroku master
   ```

5. **Open your app:**
   ```bash
   heroku open
   ```

## Option 3: Deploy with Docker (Any Cloud)

1. **Build the Docker image:**
   ```bash
   docker build -t shipping-gui .
   ```

2. **Run locally to test:**
   ```bash
   docker run -p 5000:5000 -e VEEQO_API_KEY=your_key -e EASYSHIP_API_KEY=your_key -e SECRET_KEY=secret shipping-gui
   ```

3. **Push to a registry (Docker Hub, AWS ECR, etc.) and deploy to your cloud provider**

## Important Notes

- The app is configured to use Gunicorn in production (see Procfile)
- Make sure all API keys are set as environment variables, never commit them to Git
- The app will run on the PORT environment variable (default 5000)
- Check logs if deployment fails - usually it's missing dependencies or env vars

## Quick Commands Reference

```bash
# Check current Git status
git status

# Add all files and commit
git add .
git commit -m "Your commit message"

# Push to GitHub
git push origin master

# View Heroku logs (if using Heroku)
heroku logs --tail
```
