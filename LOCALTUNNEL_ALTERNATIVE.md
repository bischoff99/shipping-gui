# LocalTunnel - Alternative to Ngrok (No Download Required!)

Since Windows Defender is blocking ngrok, let's use LocalTunnel instead. It works through npm and doesn't require downloading executables.

## Prerequisites

Check if you have Node.js:
```powershell
node --version
```

If not installed, get it from: https://nodejs.org/

## Install LocalTunnel (1 minute)

Open PowerShell and run:
```powershell
npm install -g localtunnel
```

## Start Your Public Tunnel (30 seconds)

Since your Docker container is on port 5001:
```powershell
lt --port 5001
```

## You'll Get a URL Like:
```
your url is: https://gentle-panda-42.loca.lt
```

## That's It! Your App is Public!

### First Time Access:
- When someone visits the URL, they'll see a warning page
- They need to enter the URL again to confirm
- This is LocalTunnel's security feature

### Advantages:
- ✅ No executable download required
- ✅ Won't trigger Windows Defender
- ✅ Completely free
- ✅ Works immediately

### Keep It Running:
- Leave the PowerShell window open
- Press Ctrl+C to stop the tunnel

### Custom Subdomain (Optional):
```powershell
lt --port 5001 --subdomain myshippingapp
```
This gives you: https://myshippingapp.loca.lt

## Alternative Command (if lt doesn't work):
```powershell
npx localtunnel --port 5001
```

This runs LocalTunnel without installing it globally!
