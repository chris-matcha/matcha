# Local Development Guide

## Redis Persistence Behavior

The app now uses Redis-based persistence to solve the "Presentation not found" error in Docker environments. Here's how it behaves in different environments:

## 🐳 Docker Environment (Production/Development)

**Configuration:**
- Redis URL: `redis://redis:6379/0` (uses Docker service name)
- Full persistence enabled
- File metadata survives container restarts

**Behavior:**
✅ Upload file → Assessment works immediately  
✅ Container restart → Assessment still works  
✅ Multiple workers → All can access same file data  
✅ No "Presentation not found" errors  

## 💻 Local Development (Without Redis)

**Configuration:**
- Redis URL: `redis://localhost:6379/0` (attempts local connection)
- Falls back to in-memory storage if Redis not available
- File metadata lost on app restart

**Behavior:**
✅ Upload file → Assessment works immediately  
⚠️ App restart → File metadata lost (need to re-upload)  
✅ Single process → All operations work normally  
✅ No crashes or errors  

## 💻 Local Development (With Redis)

**Configuration:**
- Redis URL: `redis://localhost:6379/0` 
- Full persistence enabled
- File metadata survives app restarts

**Behavior:**
✅ Upload file → Assessment works immediately  
✅ App restart → Assessment still works  
✅ Same experience as Docker  

## Installation Options

### Option 1: Basic Local Development (No Redis)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

**Pros:** Simple setup, no external dependencies  
**Cons:** File metadata lost on restart  

### Option 2: Full Local Development (With Redis)
```bash
# Install Redis (macOS)
brew install redis
brew services start redis

# Or install Redis (Ubuntu/Debian)
sudo apt-get install redis-server
sudo systemctl start redis

# Install Python dependencies (includes redis package)
pip install -r requirements.txt

# Run the app
python app.py
```

**Pros:** Full persistence, same as production  
**Cons:** Requires Redis installation  

## Environment Detection

The app automatically detects the environment:

```python
def get_redis_url():
    """Auto-detect environment and use appropriate Redis URL"""
    try:
        import socket
        socket.gethostbyname('redis')
        # In Docker, use the redis service name
        return 'redis://redis:6379/0'
    except socket.gaierror:
        # Local development, try localhost
        return 'redis://localhost:6379/0'
```

## Fallback Behavior

If Redis connection fails (common in local development):

1. **Graceful Degradation:** App continues to work normally
2. **In-Memory Storage:** Uses Python dictionary for file metadata
3. **No Errors:** No crashes or exceptions
4. **Full Functionality:** All features work except persistence across restarts

## Recommended Workflow

### For Quick Testing/Development:
1. `python app.py` (uses in-memory fallback)
2. Upload and test files normally
3. Restart app if needed (will lose file metadata)

### For Production-Like Testing:
1. Install and start Redis locally
2. `python app.py` (uses Redis persistence)
3. Upload and test files
4. Restart app - files still accessible

### For Production Deployment:
1. Use Docker Compose (includes Redis)
2. `docker-compose up -d`
3. Full persistence and multi-worker support

## Troubleshooting

### "Presentation not found" errors:
- **Docker:** Should not occur with the new implementation
- **Local without Redis:** Can occur after app restart
- **Local with Redis:** Should not occur

### Redis connection issues:
- Check if Redis is running: `redis-cli ping`
- Check connection logs in app startup
- App will fallback to in-memory storage automatically

### Performance considerations:
- **In-memory:** Faster access, no network overhead
- **Redis:** Slightly slower, but persistent and shareable

## Summary

✅ **The app works in all environments**  
✅ **No configuration changes needed**  
✅ **Automatic environment detection**  
✅ **Graceful fallback behavior**  
✅ **Docker issues completely resolved**  

Choose your setup based on your needs:
- **Basic local dev:** Just run `python app.py`
- **Full local dev:** Install Redis + run `python app.py`
- **Production:** Use Docker Compose