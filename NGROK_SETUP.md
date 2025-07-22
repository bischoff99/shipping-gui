# Ngrok Setup - Get Your App Online in 2 Minutes!

## Step 1: Download Ngrok

1. Visit: https://ngrok.com/download
2. Download the Windows version
3. Extract the ZIP file to a folder (e.g., `C:\ngrok`)

## Step 2: Sign Up for Free Account

1. Go to: https://ngrok.com/signup
2. Create a free account
3. Get your auth token from: https://dashboard.ngrok.com/get-started/your-authtoken

## Step 3: Configure Ngrok

Open PowerShell and navigate to where you extracted ngrok:
```powershell
cd C:\ngrok
```

Add your auth token:
```powershell
.\ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

## Step 4: Expose Your App

Since your Docker container is running on port 5001:
```powershell
.\ngrok http 5001
```

## Step 5: Your Public URL

Ngrok will display something like:
```
Session Status                online
Account                       your-email@example.com (Plan: Free)
Version                       3.0.0
Region                        United States (us)
Latency                       50ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123xyz.ngrok-free.app -> http://localhost:5001
```

Your app is now accessible at: `https://abc123xyz.ngrok-free.app`

## Important Notes:

- **Free tier limitations**:
  - URL changes each time you restart ngrok
  - Limited to 40 connections per minute
  - Shows ngrok splash page (can be bypassed)

- **Keep ngrok running**: The tunnel stays active as long as the ngrok process runs

- **Share the HTTPS URL**: Anyone can access your app through the ngrok URL

## Quick Start Commands:

```powershell
# If ngrok is in your PATH:
ngrok http 5001

# If not, use full path:
C:\ngrok\ngrok.exe http 5001
```

## Monitoring:
- Visit http://127.0.0.1:4040 to see request inspector
- Monitor all incoming requests in real-time

That's it! Your shipping GUI is now publicly accessible!
