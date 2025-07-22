# Deployment Guide

## Prerequisites
- Git installed
- Heroku CLI (for Heroku deployment)
- Python 3.11+

## Heroku Deployment

1. Create a Heroku account and install Heroku CLI
2. Login to Heroku:
   ```bash
   heroku login
   ```

3. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```

4. Set environment variables:
   ```bash
   heroku config:set VEEQO_API_KEY=your-veeqo-key
   heroku config:set EASYSHIP_API_KEY=your-easyship-key
   heroku config:set SECRET_KEY=your-secret-key
   ```

5. Deploy:
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push heroku main
   ```

## Alternative: Deploy to VPS (Ubuntu/Debian)

1. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx
   ```

2. Clone your repository and setup virtual environment:
   ```bash
   cd /var/www
   git clone your-repo-url
   cd shipping-gui
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Create systemd service file:
   ```bash
   sudo nano /etc/systemd/system/shipping-gui.service
   ```

4. Start the service:
   ```bash
   sudo systemctl start shipping-gui
   sudo systemctl enable shipping-gui
   ```

## Environment Variables
Copy `.env.example` to `.env` and fill in your actual values.
