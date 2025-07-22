# Ngrok Step-by-Step Guide - Make Your App Public Now!

## Current Status:
- ✅ Your app is running on Docker (port 5001)
- ✅ Accessible locally at http://localhost:5001
- 🎯 Next: Make it publicly accessible with ngrok

## Step 1: Download Ngrok (2 minutes)

1. Go to the download page (already opened)
2. Click "Download for Windows"
3. Save the ZIP file
4. Extract it to `C:\ngrok` (or any folder you prefer)

## Step 2: Get Your Free Auth Token (2 minutes)

1. Sign up at: https://ngrok.com/signup
2. After login, go to: https://dashboard.ngrok.com/get-started/your-authtoken
3. Copy your auth token (looks like: `2abc123XYZ...`)

## Step 3: Configure Ngrok (1 minute)

Open PowerShell and run:
```powershell
cd C:\ngrok
.\ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

## Step 4: Create Public Tunnel (30 seconds)

In the same PowerShell window:
```powershell
.\ngrok http 5001
```

## Step 5: Get Your Public URL

You'll see output like:
```
Session Status                online
Account                       your@email.com (Plan: Free)
Update                        Update available (version 3.0.1, Ctrl-U to update)
Version                       3.0.0
Region                        United States (us)
Latency                       52ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://84c5df474.ngrok-free.app -> http://localhost:5001

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

## 🎉 YOUR APP IS NOW LIVE AT: `https://84c5df474.ngrok-free.app`

## What You Can Do Now:

1. **Share the URL** - Anyone can access your shipping GUI
2. **Monitor Traffic** - Visit http://127.0.0.1:4040 in your browser
3. **Keep it Running** - The tunnel stays active while ngrok runs

## Quick Troubleshooting:

**"Page not loading"**
- Make sure Docker container is running: `docker ps`
- Check if using port 5001: `.\ngrok http 5001`

**"Tunnel expired"**
- Just run `.\ngrok http 5001` again
- Free URLs change each time

**"Connection refused"**
- Start Docker container: `docker start shipping-gui-container`
- Wait 30 seconds for it to fully start

## Pro Tips:

- Save the ngrok URL before sharing
- The free tier is perfect for demos and testing
- Keep PowerShell window open to maintain tunnel
- Press Ctrl+C to stop the tunnel

## Alternative: Use the Helper Script

Instead of manual steps, just run:
```powershell
powershell -ExecutionPolicy Bypass -File "run_ngrok.ps1"
```

This script will guide you through everything!
