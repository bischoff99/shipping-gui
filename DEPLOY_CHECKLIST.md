# 🚀 Quick Deployment Checklist

## Option 1: Railway (Easiest - No CLI Required!)

### ✅ Prerequisites Check:
- [x] Git initialized (Already done!)
- [x] All files committed to Git (Already done!)
- [ ] GitHub account created
- [ ] Code pushed to GitHub
- [ ] API keys ready

### 📋 Step-by-Step:

1. **Create GitHub Repository**
   - [ ] Go to https://github.com/new
   - [ ] Name: `shipping-gui`
   - [ ] DON'T check "Add README"
   - [ ] Click "Create repository"

2. **Push Code to GitHub**
   - [ ] Run the helper script:
   ```powershell
   powershell -ExecutionPolicy Bypass -File "setup_github.ps1"
   ```

3. **Deploy on Railway**
   - [ ] Visit https://railway.app
   - [ ] Login with GitHub
   - [ ] New Project → Deploy from GitHub
   - [ ] Select your repository
   - [ ] Add environment variables:
     - VEEQO_API_KEY
     - EASYSHIP_API_KEY
     - SECRET_KEY

4. **Done!** Your app will be live at `yourapp.railway.app`

---

## Option 2: Local Testing First

If you want to test locally before deploying:

```powershell
# Make sure Flask app is running
python app.py

# Visit http://localhost:5000
```

---

## 🔑 Environment Variables You'll Need:

```
VEEQO_API_KEY = (get from Veeqo dashboard)
EASYSHIP_API_KEY = (get from Easyship dashboard)
SECRET_KEY = (any random string, e.g.: mysecretkey123)
```

---

## 📚 Deployment Guides:

- **Railway**: See `RAILWAY_QUICK_DEPLOY.md`
- **Heroku**: See `HEROKU_DEPLOY_STEPS.md` (requires CLI)
- **GitHub Setup**: Run `setup_github.ps1`
