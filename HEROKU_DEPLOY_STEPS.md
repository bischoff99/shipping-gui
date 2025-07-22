# Heroku Deployment Steps for Shipping GUI

## Step 1: Install Heroku CLI

1. Visit: https://devcenter.heroku.com/articles/heroku-cli
2. Click on "Download and install" for Windows
3. Download the 64-bit installer
4. Run the installer (it will install Git as well if not already installed)
5. Restart your terminal/PowerShell after installation

## Step 2: Verify Installation

Open a new PowerShell terminal and run:
```bash
heroku --version
```

## Step 3: Login to Heroku

```bash
heroku login
```
This will open your browser for authentication.

## Step 4: Create Heroku App

Navigate to your project directory:
```bash
cd "c:\Users\Zubru\shipping gui"
```

Create a new Heroku app (replace 'your-app-name' with a unique name):
```bash
heroku create your-app-name
```

Example:
```bash
heroku create shipping-gui-2024
```

## Step 5: Set Environment Variables

Set your API keys (replace with your actual keys):

```bash
heroku config:set VEEQO_API_KEY=your_actual_veeqo_api_key
heroku config:set EASYSHIP_API_KEY=your_actual_easyship_api_key
heroku config:set SECRET_KEY=generate_a_random_secret_key_here
```

To generate a random secret key, you can use:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

## Step 6: Deploy to Heroku

Push your code to Heroku:
```bash
git push heroku master
```

## Step 7: Ensure at least one dyno is running

```bash
heroku ps:scale web=1
```

## Step 8: Open your app

```bash
heroku open
```

## Troubleshooting Commands

View logs:
```bash
heroku logs --tail
```

Check app status:
```bash
heroku ps
```

Restart app:
```bash
heroku restart
```

View config vars:
```bash
heroku config
```

## Quick Reference - All Commands in Order

```bash
# 1. Login
heroku login

# 2. Create app
heroku create your-unique-app-name

# 3. Set environment variables
heroku config:set VEEQO_API_KEY=your_key
heroku config:set EASYSHIP_API_KEY=your_key
heroku config:set SECRET_KEY=your_secret

# 4. Deploy
git push heroku master

# 5. Scale
heroku ps:scale web=1

# 6. Open
heroku open
```

## Important Notes

- Your app name must be unique across all of Heroku
- Free tier includes 550-1000 dyno hours per month
- The app will sleep after 30 minutes of inactivity on free tier
- Make sure your `requirements.txt` includes all dependencies
- The `Procfile` is already configured to use Gunicorn
- Default port is handled by Heroku (via PORT environment variable)

## Next Steps After Deployment

1. Visit your app at: https://your-app-name.herokuapp.com
2. Monitor logs: `heroku logs --tail`
3. Set up a custom domain (optional): `heroku domains:add www.yourdomain.com`
4. Enable SSL (included free with Heroku)
5. Set up database if needed: `heroku addons:create heroku-postgresql:hobby-dev`
