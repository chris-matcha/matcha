# Railway Deployment Guide for Matcha

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI** (optional): Install with `brew install railway` or `npm install -g @railway/cli`
3. **GitHub Repository**: Your code should be pushed to GitHub (✅ Already done!)

## Method 1: Deploy from GitHub (Recommended)

### Step 1: Connect GitHub to Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub account
5. Select your repository: `chris-matcha/matcha`

### Step 2: Configure Environment Variables

In Railway dashboard:
1. Click on your project
2. Go to "Variables" tab
3. Add your environment variables:

```env
ANTHROPIC_API_KEY=your_actual_api_key_here
FLASK_ENV=production
PYTHONUNBUFFERED=1
PORT=8000
```

### Step 3: Add Redis Service

1. In your Railway project, click "+ New"
2. Select "Database" → "Add Redis"
3. Railway will automatically create a Redis instance
4. The Redis URL will be automatically injected as `REDIS_URL`

### Step 4: Configure Deployment Settings

1. Go to "Settings" → "Deploy"
2. Set the following:
   - **Root Directory**: `/` (default)
   - **Build Command**: Leave empty (uses Dockerfile)
   - **Start Command**: Leave empty (uses Dockerfile CMD)

### Step 5: Update Your Code for Railway

Create a `railway.json` file in your project root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 60,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Step 6: Update Dockerfile for Railway

Railway uses PORT environment variable. Update your Dockerfile's CMD:

```dockerfile
# Replace the last line in your Dockerfile with:
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120 --access-logfile - --error-logfile - app:app
```

### Step 7: Update app.py for Railway's PORT

Add this to the bottom of your app.py:

```python
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
```

## Method 2: Deploy Using Railway CLI

### Step 1: Install and Login

```bash
# Install Railway CLI
brew install railway  # or npm install -g @railway/cli

# Login
railway login
```

### Step 2: Initialize Project

```bash
cd /Users/chris/projects/GitHub/Matcha

# Initialize Railway project
railway init

# Link to existing project (if you created one in the UI)
railway link
```

### Step 3: Add Services

```bash
# Add Redis
railway add redis

# Deploy
railway up
```

### Step 4: Set Environment Variables

```bash
railway variables set ANTHROPIC_API_KEY=your_api_key_here
railway variables set FLASK_ENV=production
railway variables set PYTHONUNBUFFERED=1
```

## Important Configuration Updates

### 1. Update Your Redis Connection

Since Railway provides `REDIS_URL` automatically, your app already handles this correctly:

```python
session_store_config = {
    'redis_url': os.getenv('REDIS_URL', get_redis_url()),
    'session_ttl_hours': 24
}
```

### 2. Update Nginx Configuration (Not needed for Railway)

Railway handles load balancing and SSL automatically. You don't need the nginx container.

### 3. Simplified docker-compose.yml for Railway

Create a `railway.dockerfile` (optional - for local testing that mirrors Railway):

```dockerfile
FROM python:3.11-slim-bullseye

# Install dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p uploads outputs logs instance

# Expose port (Railway sets this)
EXPOSE ${PORT:-8000}

# Run gunicorn with Railway's PORT
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120 --access-logfile - --error-logfile - app:app
```

## Deployment Steps Summary

1. **Push these changes to GitHub**:
   ```bash
   git add railway.json
   git commit -m "Add Railway deployment configuration"
   git push origin main
   ```

2. **In Railway Dashboard**:
   - Connect GitHub repo
   - Add Redis service
   - Set environment variables
   - Deploy!

3. **Monitor Deployment**:
   - Check build logs in Railway dashboard
   - Visit the generated URL (format: `your-app.railway.app`)
   - Monitor health at `your-app.railway.app/health`

## Environment Variables Checklist

Required in Railway:
- [x] `ANTHROPIC_API_KEY` - Your Anthropic API key
- [x] `PORT` - Set automatically by Railway
- [x] `REDIS_URL` - Set automatically when you add Redis

Optional:
- [ ] `FLASK_ENV` - Set to `production`
- [ ] `PYTHONUNBUFFERED` - Set to `1`

## Troubleshooting

### Common Issues:

1. **Build Fails**: Check Dockerfile syntax and requirements.txt
2. **App Crashes**: Check logs for missing environment variables
3. **Redis Connection**: Railway provides REDIS_URL automatically
4. **Port Issues**: Ensure using `${PORT}` environment variable

### View Logs:

```bash
railway logs
```

Or check logs in the Railway dashboard.

## Cost Estimation

Railway pricing (as of 2024):
- **Hobby Plan**: $5/month (includes $5 of usage)
- **Redis**: ~$5-10/month depending on usage
- **Total**: ~$10-15/month for a small app

## Next Steps

1. Add custom domain (in Railway settings)
2. Set up monitoring/alerts
3. Configure automatic deploys from GitHub
4. Add backup strategy for Redis data

## Security Notes

- Never commit `.env` file with real API keys
- Use Railway's environment variables for secrets
- Enable 2FA on your Railway account
- Regularly rotate API keys