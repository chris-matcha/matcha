# Railway Deployment Checklist

## Quick Deployment Steps

### 1. Push Railway Configuration to GitHub
```bash
git add railway.json Dockerfile app.py RAILWAY_DEPLOYMENT_GUIDE.md
git commit -m "Add Railway deployment configuration"
git push origin main
```

### 2. Deploy on Railway Website

1. **Go to [railway.app](https://railway.app)**
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose `chris-matcha/matcha`**
5. **Add Redis**: Click "+ New" → "Database" → "Redis"
6. **Set Environment Variables**:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   FLASK_ENV=production
   ```

### 3. Wait for Deployment

- Railway will automatically:
  - Build your Docker image
  - Deploy your application
  - Set up Redis with REDIS_URL
  - Provide a public URL

### 4. Test Your Deployment

1. Visit: `https://your-app.railway.app`
2. Check health: `https://your-app.railway.app/health`
3. Test file upload and adaptation

## Environment Variables Summary

| Variable | Required | Source | Example |
|----------|----------|--------|---------|
| ANTHROPIC_API_KEY | ✅ Yes | You provide | sk-ant-... |
| REDIS_URL | ✅ Yes | Railway provides | redis://... |
| PORT | ✅ Yes | Railway provides | 8000 |
| FLASK_ENV | Optional | You provide | production |

## Monitoring

- **Build Logs**: Check in Railway dashboard
- **Runtime Logs**: `railway logs` or dashboard
- **Health Check**: `/health` endpoint
- **Redis Status**: Check Redis service in dashboard

## Common Issues & Solutions

1. **Build fails**: Check `requirements.txt` for typos
2. **App crashes**: Verify ANTHROPIC_API_KEY is set
3. **Redis errors**: Railway auto-configures REDIS_URL
4. **502 errors**: Check if app is binding to PORT

## Success Indicators

✅ Green "Active" status in Railway  
✅ Health endpoint returns `{"status": "healthy"}`  
✅ Can upload and process files  
✅ Progress bars work correctly  

## Next Steps After Deployment

1. **Custom Domain**: Settings → Domains → Add custom domain
2. **Monitoring**: Set up alerts in Railway
3. **Scaling**: Adjust worker count if needed
4. **Backups**: Configure Redis persistence