    # Railway Deployment - Exact Step-by-Step Guide

## What You Need to Do (5 minutes max):

### Step 1: Go to Your Railway Dashboard
- You should already be logged in at https://railway.app
- You should see your `shipping-gui` project

### Step 2: Click on Your Project
- Click on the `shipping-gui` project card
- You'll see your deployment

### Step 3: Add Environment Variables
1. Click on your service (it might be called "web" or show your repo name)
2. Click the "Variables" tab (usually on the right side)
3. Click "Raw Editor" button (it's easier than adding one by one)
4. DELETE any existing text in the box
5. PASTE this entire block exactly:

```
VEEQO_API_KEY=Vqt/7a55360df188537a330a977ef0034942
EASYSHIP_API_KEY=prod_VC6QKi48mtqwXpXJubfmT/MsOmzTIG0Qyd89/X61ylc=
SECRET_KEY=unified_order_system_2025_production_secret_key_v2
```

6. Click "Save" or "Update Variables"

### Step 4: Wait for Automatic Redeploy
- Railway will show "Deploying..." 
- Wait 1-2 minutes
- Look for green checkmark ✓

### Step 5: Get Your App URL
- In the same service view, look at the top
- You'll see a URL like: `shipping-gui-production.up.railway.app`
- Click on it to open your live app!

## If You Don't See Your Project:

1. Make sure you're logged into Railway with GitHub
2. Click "New Project" 
3. Select "Deploy from GitHub repo"
4. Choose `bischoff99/shipping-gui`
5. Railway will start deploying
6. Then follow steps 3-5 above

## What Success Looks Like:
- Green checkmark on deployment
- In Logs tab: "Running on http://0.0.0.0:5000"
- Your app loads when you visit the URL
- You see the shipping GUI interface

## Common Issues:
- If you see "Application failed to respond":
  - Check if all 3 environment variables are added
  - Look at Logs tab for errors
- If deployment fails:
  - Make sure variables are copied exactly (no extra spaces)
  - Check that your GitHub repo is up to date

## Need the Variables Again?
```
VEEQO_API_KEY=Vqt/7a55360df188537a330a977ef0034942
EASYSHIP_API_KEY=prod_VC6QKi48mtqwXpXJubfmT/MsOmzTIG0Qyd89/X61ylc=
SECRET_KEY=unified_order_system_2025_production_secret_key_v2
```

That's it! Your app will be live in minutes!
