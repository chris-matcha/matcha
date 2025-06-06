# Matcha Application Deployment Guide

## Overview
This guide covers deploying the Matcha adaptive learning application to production. The app includes authentication, file processing, and AI-powered content adaptation.

## Security Checklist

### ✅ Already Implemented
- User authentication with Flask-Login
- Password hashing with bcrypt
- CSRF protection with Flask-WTF
- Rate limiting on sensitive endpoints
- Input sanitization
- Security headers (X-Frame-Options, CSP, etc.)
- File upload validation

### ⚠️ Required Before Deployment
1. **Change default admin password** in `auth.py` line 139
2. **Generate new SECRET_KEY** for production
3. **Set up HTTPS** (required for production)
4. **Configure environment variables** properly
5. **Disable debug mode** in production
6. **Set up proper logging**
7. **Configure backup strategy** for SQLite database

## Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Prerequisites
- Docker and Docker Compose installed
- Domain name with SSL certificate
- At least 2GB RAM

#### Steps

1. **Clone and prepare the repository**
```bash
git clone <your-repo-url>
cd Matcha
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your production values
# IMPORTANT: Generate a secure SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

3. **Generate SSL certificates** (for testing, use self-signed)
```bash
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem
```

4. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

5. **Initialize the database**
```bash
docker-compose exec web python -c "from auth import User; User.init_db()"
```

6. **Create admin user with secure password**
```bash
docker-compose exec web python -c "
from auth import User
User.create_user('admin', 'admin@yourdomain.com', 'your-secure-password')
"
```

### Option 2: VPS Deployment (Ubuntu/Debian)

#### Prerequisites
- Ubuntu 20.04+ or Debian 11+
- Python 3.9+
- Nginx
- Supervisor (for process management)

#### Steps

1. **System setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx supervisor redis-server \
  poppler-utils libmagic1 -y
```

2. **Create application user**
```bash
sudo useradd -m -s /bin/bash matcha
sudo su - matcha
```

3. **Set up application**
```bash
# Clone repository
git clone <your-repo-url> ~/matcha
cd ~/matcha

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

4. **Configure Supervisor**
```bash
# Create supervisor config
sudo nano /etc/supervisor/conf.d/matcha.conf
```

Add:
```ini
[program:matcha]
command=/home/matcha/matcha/venv/bin/gunicorn -c gunicorn_config.py app:app
directory=/home/matcha/matcha
user=matcha
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/matcha/app.log
environment="PATH=/home/matcha/matcha/venv/bin",FLASK_ENV="production"
```

5. **Configure Nginx**
```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/matcha
sudo ln -s /etc/nginx/sites-available/matcha /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

6. **Start application**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start matcha
```

### Option 3: Platform-as-a-Service Deployment

#### Heroku Deployment

1. **Create `Procfile`**
```
web: gunicorn app:app
```

2. **Create `runtime.txt`**
```
python-3.11.7
```

3. **Deploy**
```bash
heroku create your-app-name
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ANTHROPIC_API_KEY=your-api-key
git push heroku main
```

#### Railway/Render Deployment

1. **Add `railway.json` or `render.yaml`**
```json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "gunicorn app:app",
    "restartPolicyType": "on-failure",
    "restartPolicyMaxRetries": 10
  }
}
```

2. Deploy via platform dashboard

## Post-Deployment

### 1. Security Hardening

```bash
# Set proper file permissions
chmod 755 ~/matcha
chmod 700 ~/matcha/instance
chmod 700 ~/matcha/uploads
chmod 700 ~/matcha/outputs

# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Monitoring Setup

- Set up application monitoring (e.g., Sentry)
- Configure log rotation
- Set up uptime monitoring
- Enable performance monitoring

### 3. Backup Strategy

```bash
# Daily database backup
0 2 * * * /usr/bin/sqlite3 /home/matcha/matcha/instance/matcha.db ".backup /home/matcha/backups/matcha-$(date +\%Y\%m\%d).db"

# Weekly file backup
0 3 * * 0 tar -czf /home/matcha/backups/files-$(date +\%Y\%m\%d).tar.gz /home/matcha/matcha/uploads /home/matcha/matcha/outputs
```

### 4. SSL Certificate (Production)

Use Let's Encrypt for free SSL:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Environment Variables

Critical environment variables for production:

```bash
# Security
SECRET_KEY=<generate-strong-key>
FLASK_ENV=production
SESSION_COOKIE_SECURE=true

# API
ANTHROPIC_API_KEY=<your-key>

# Database
DATABASE_URL=sqlite:///instance/matcha.db

# Redis (for rate limiting)
RATELIMIT_STORAGE_URL=redis://localhost:6379

# CORS (update with your domain)
CORS_ORIGINS=https://yourdomain.com
```

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   - Check file ownership: `chown -R matcha:matcha /home/matcha/matcha`
   - Check directory permissions

2. **502 Bad Gateway**
   - Check if gunicorn is running: `sudo supervisorctl status`
   - Check logs: `tail -f /var/log/matcha/app.log`

3. **File Upload Issues**
   - Verify upload directory exists and is writable
   - Check nginx client_max_body_size setting

4. **Database Locked**
   - Ensure only one process accesses SQLite at a time
   - Consider upgrading to PostgreSQL for high traffic

## Performance Optimization

1. **Enable caching** for static assets
2. **Use CDN** for static files
3. **Enable gzip compression** in nginx
4. **Consider PostgreSQL** for better concurrency
5. **Add Redis** for session storage and caching

## Security Considerations

1. **Regular Updates**
   - Keep system packages updated
   - Monitor for security advisories
   - Update Python dependencies regularly

2. **Access Control**
   - Implement IP whitelisting if needed
   - Use fail2ban for brute force protection
   - Regular security audits

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Regular backups with encryption
   - Implement data retention policies

## Support

For deployment issues:
1. Check application logs
2. Review nginx error logs
3. Verify environment variables
4. Test with minimal configuration first

Remember to always test deployment in a staging environment before production!