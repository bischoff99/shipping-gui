# Docker Deployment Guide - Deploy Your Shipping GUI

Your Docker image `shipping-gui` is built and ready. Here are the best deployment options:

## Option 1: Docker Hub + Cloud Run (Google) - EASIEST

### Step 1: Push to Docker Hub
```powershell
# 1. Create account at https://hub.docker.com
# 2. Login to Docker Hub
docker login

# 3. Tag your image
docker tag shipping-gui YOUR_DOCKERHUB_USERNAME/shipping-gui:latest

# 4. Push to Docker Hub
docker push YOUR_DOCKERHUB_USERNAME/shipping-gui:latest
```

### Step 2: Deploy to Google Cloud Run (Free tier available)
1. Go to: https://console.cloud.google.com/run
2. Click "Create Service"
3. Select "Deploy one revision from an existing container image"
4. Enter: `docker.io/YOUR_DOCKERHUB_USERNAME/shipping-gui:latest`
5. Set environment variables:
   - VEEQO_API_KEY
   - EASYSHIP_API_KEY
   - SECRET_KEY
6. Click "Create"

## Option 2: Railway with Docker

1. Push to Docker Hub (as above)
2. Go to https://railway.app
3. New Project → Deploy Docker Image
4. Enter your Docker Hub image URL
5. Add environment variables
6. Deploy!

## Option 3: DigitalOcean App Platform

1. Push to Docker Hub
2. Go to https://cloud.digitalocean.com/apps
3. Create App → Docker Hub
4. Select your repository
5. Add environment variables
6. Deploy ($5/month)

## Option 4: Render.com (Free tier)

1. Push to Docker Hub
2. Go to https://render.com
3. New → Web Service
4. Connect Docker Hub
5. Free tier available!

## Option 5: Azure Container Instances

```powershell
# Install Azure CLI first
# Then:
az login
az group create --name myResourceGroup --location eastus
az container create --resource-group myResourceGroup --name shipping-gui --image YOUR_DOCKERHUB_USERNAME/shipping-gui:latest --ports 5000 --environment-variables VEEQO_API_KEY=your_key EASYSHIP_API_KEY=your_key SECRET_KEY=your_secret
```

## Quick Start Commands

### 1. First, check your Docker image:
```powershell
docker images
```

### 2. Test locally one more time:
```powershell
docker run -p 5000:5000 -e VEEQO_API_KEY=your_key -e EASYSHIP_API_KEY=your_key -e SECRET_KEY=your_secret shipping-gui
```

### 3. Create Docker Hub account:
https://hub.docker.com/signup

### 4. Push to Docker Hub:
```powershell
docker login
docker tag shipping-gui YOUR_USERNAME/shipping-gui:latest
docker push YOUR_USERNAME/shipping-gui:latest
```

## Environment Variables for All Platforms:
```
VEEQO_API_KEY=Vqt/7a55360df188537a330a977ef0034942
EASYSHIP_API_KEY=prod_VC6QKi48mtqwXpXJubfmT/MsOmzTIG0Qyd89/X61ylc=
SECRET_KEY=unified_order_system_2025_production_secret_key_v2
```

## Recommended: Google Cloud Run
- Free tier: 2 million requests/month
- Automatic HTTPS
- Scales to zero (saves money)
- Easy deployment
- No credit card required for free tier
