# Railway Environment Variables - Quick Copy & Paste

## Your Environment Variables (Ready to Copy)

Copy and paste these into Railway's Variables section:

### 1. VEEQO_API_KEY
```
Vqt/7a55360df188537a330a977ef0034942
```

### 2. EASYSHIP_API_KEY
```
prod_VC6QKi48mtqwXpXJubfmT/MsOmzTIG0Qyd89/X61ylc=
```

### 3. SECRET_KEY
```
unified_order_system_2025_production_secret_key_v2
```

## Quick Setup Steps in Railway:

1. In your Railway dashboard, click on your deployed app
2. Go to "Variables" tab
3. Click "Raw Editor" (easier for multiple variables)
4. Paste this exactly:

```
VEEQO_API_KEY=Vqt/7a55360df188537a330a977ef0034942
EASYSHIP_API_KEY=prod_VC6QKi48mtqwXpXJubfmT/MsOmzTIG0Qyd89/X61ylc=
SECRET_KEY=unified_order_system_2025_production_secret_key_v2
```

5. Click "Save"
6. Railway will automatically redeploy your app

## Your App Will Be Live At:
`https://[your-app-name].railway.app`

## Check Deployment Status:
- Look for green checkmark in Railway dashboard
- Click "Logs" to see if app started successfully
- Should see: "Running on http://0.0.0.0:5000" in logs

That's it! Your shipping GUI will be live in about 1-2 minutes!
