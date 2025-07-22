#!/bin/bash
# Quick Production Deployment Script

echo "🚀 Unified Order Management - Production Deployment"
echo "=================================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📋 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - Production ready Flask app"
fi

echo ""
echo "🌐 Choose your deployment platform:"
echo "1. Heroku (Easiest)"
echo "2. Railway (Modern)"
echo "3. DigitalOcean (Scalable)"
echo "4. Docker Build (Any cloud)"
echo "5. AWS (Enterprise)"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "🚀 Deploying to Heroku..."
        echo "Run these commands:"
        echo "heroku create your-app-name"
        echo "heroku config:set FLASK_SECRET_KEY=$(openssl rand -hex 32)"
        echo "git push heroku main"
        ;;
    2)
        echo "🚀 Railway deployment:"
        echo "1. Visit https://railway.app"
        echo "2. Connect this GitHub repo"
        echo "3. Set environment variables"
        echo "4. Deploy automatically"
        ;;
    3)
        echo "🚀 DigitalOcean App Platform:"
        echo "1. Visit https://cloud.digitalocean.com/apps"
        echo "2. Create new app from GitHub"
        echo "3. Use the .do/app.yaml configuration"
        ;;
    4)
        echo "🐳 Building Docker image..."
        docker build -t unified-order-system .
        echo "Docker image built! Push to your registry."
        ;;
    5)
        echo "☁️ AWS deployment requires additional setup"
        echo "Consider using AWS Elastic Beanstalk or ECS"
        ;;
esac

echo ""
echo "✅ Deployment files are ready!"
echo "📁 Check the deployment guides in your project folder"
