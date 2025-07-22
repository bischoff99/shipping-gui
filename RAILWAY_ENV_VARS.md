# Railway Environment Variables Setup

## Required Environment Variables

Once your app is deployed on Railway, you need to add these environment variables:

### 1. VEEQO_API_KEY
- **Description**: Your Veeqo API key for order management
- **How to get it**: 
  - Login to your Veeqo account
  - Go to Settings → API Keys
  - Create a new API key or use existing one
- **Example**: `veeqo_api_key_abc123xyz789`

### 2. EASYSHIP_API_KEY
- **Description**: Your Easyship API key for shipping integration
- **How to get it**:
  - Login to your Easyship account
  - Go to Settings → API & Integrations
  - Generate an API key
- **Example**: `es_live_abc123xyz789`

### 3. SECRET_KEY
- **Description**: Flask secret key for session security
- **How to generate**: Use any random string or generate one:
  ```python
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- **Example**: `a8f5f167f44f4964e6c998dee827110c85d8c5c1f7d3b4e6a9c8b3d2e1f0a9b8`

## How to Add Variables in Railway

1. **Go to your Railway project dashboard**
2. **Click on your deployed service**
3. **Navigate to the "Variables" tab**
4. **Click "Add Variable"**
5. **Add each variable:**
   - Name: `VEEQO_API_KEY`
   - Value: `your_actual_veeqo_key`
   - Click "Add"
6. **Repeat for all variables**
7. **Railway will automatically redeploy with new variables**

## Testing Your Deployment

After adding all variables, your app should be live at:
`https://your-app-name.railway.app`

Check the deployment logs in Railway dashboard to ensure everything is running correctly.

## Troubleshooting

If your app doesn't work after adding variables:
1. Check the "Logs" tab in Railway for errors
2. Ensure all variable names are EXACTLY as shown above
3. Make sure there are no extra spaces in the values
4. Verify your API keys are active and valid