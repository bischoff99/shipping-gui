# Railway Deployment - No CLI Required!

Railway is a modern deployment platform that works entirely through your web browser. No command-line tools needed!

## Step 1: Push Your Code to GitHub

1. **Create a GitHub account** (if you don't have one):
   - Visit: https://github.com/signup

2. **Create a new repository on GitHub**:
   - Go to: https://github.com/new
   - Name it: `shipping-gui` (or any name you prefer)
   - Keep it Private or Public (your choice)
   - DON'T initialize with README (you already have one)
   - Click "Create repository"

3. **Push your code** - Run these commands in PowerShell:
   ```bash
   cd "c:\Users\Zubru\shipping gui"
   git remote add origin https://github.com/YOUR_USERNAME/shipping-gui.git
   git branch -M main
   git push -u origin main
   ```
   Replace `YOUR_USERNAME` with your GitHub username!

## Step 2: Deploy on Railway

1. **Visit Railway**: https://railway.app

2. **Sign up/Login** with your GitHub account

3. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `shipping-gui` repository
   - Railway will automatically detect it's a Flask app!

4. **Add Environment Variables**:
   - Click on your deployed service
   - Go to "Variables" tab
   - Click "Add Variable" and add these:
     ```
     VEEQO_API_KEY = your_veeqo_api_key_here
     EASYSHIP_API_KEY = your_easyship_api_key_here
     SECRET_KEY = any_random_string_for_security
     ```

5. **Deploy**:
   - Railway will automatically deploy your app
   - You'll get a URL like: `yourapp.railway.app`

## That's it! 🎉

Your app will be live in about 2-3 minutes!

## Benefits of Railway:
- ✅ No CLI installation required
- ✅ Automatic HTTPS
- ✅ Free tier available
- ✅ Auto-deploy on git push
- ✅ Easy environment variables management
- ✅ Built-in logging and monitoring

## After Deployment:
- Your app URL will be shown in Railway dashboard
- Check deployment logs in the Railway dashboard
- Any future changes: just push to GitHub and Railway auto-deploys!
