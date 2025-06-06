# Matcha Security Setup Guide

This guide walks you through setting up the secure version of Matcha with authentication and security hardening while running locally.

## Quick Start

### 1. Install Dependencies
```bash
# Install new security dependencies
pip install -r requirements.txt
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (especially ANTHROPIC_API_KEY)
nano .env
```

### 3. Run Secure Application
```bash
# Run the secure version
python secure_app.py
```

### 4. Access Application
- Open browser to: http://127.0.0.1:5000
- **Default Login:** username: `admin`, password: `admin123`
- **⚠️ IMPORTANT:** Change default password immediately!

## Security Features Implemented

### ✅ Authentication & Authorization
- **Flask-Login** user session management
- **Password hashing** with Werkzeug
- **Session timeout** (1 hour default)
- **Login required** for all main features

### ✅ Input Validation & Sanitization
- **Flask-WTF forms** with CSRF protection
- **File upload validation** (type, size, content)
- **Input sanitization** for XSS prevention
- **Email validation**

### ✅ Rate Limiting
- **Login attempts:** 5 per minute
- **File uploads:** 10 per minute  
- **API calls:** 30 per minute
- **General requests:** 100 per hour

### ✅ Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Content-Security-Policy` (basic)

### ✅ Secure File Handling
- **Filename sanitization**
- **File type validation**
- **Content verification** (magic numbers)
- **Upload size limits** (50MB)
- **Secure file storage**

## Default Users

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Administrator |

## Environment Variables

Required variables in `.env`:

```bash
# Essential
SECRET_KEY=your-long-random-secret-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key

# Optional (has defaults)
FLASK_ENV=development
SESSION_TIMEOUT=3600
```

## File Structure Changes

```
/Matcha/
├── secure_app.py          # 🆕 Secure Flask application
├── auth.py                # 🆕 User authentication system
├── forms.py               # 🆕 WTF forms with validation
├── security_config.py     # 🆕 Security configuration
├── templates/             # 🆕 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── upload.html
├── instance/              # 🆕 Database folder
│   └── matcha.db         # SQLite user database
├── .env.example          # 🆕 Environment template
└── requirements.txt      # ✏️ Updated with security deps
```

## Testing Security Features

### 1. Test Authentication
```bash
# Try accessing protected routes without login
curl http://127.0.0.1:5000/upload
# Should redirect to login

# Test rate limiting
curl -X POST http://127.0.0.1:5000/login \
     -d "username=wrong&password=wrong" \
     --cookie-jar cookies.txt
# Repeat 6+ times to trigger rate limit
```

### 2. Test File Upload Security
```bash
# Try uploading invalid file type
curl -X POST http://127.0.0.1:5000/upload \
     -F "file=@malicious.exe" \
     --cookie cookies.txt
# Should be rejected
```

### 3. Test CSRF Protection
```bash
# Try POST without CSRF token
curl -X POST http://127.0.0.1:5000/register \
     -d "username=test&email=test@test.com&password=password123"
# Should be rejected with 400 error
```

## Common Issues & Solutions

### Issue: "ANTHROPIC_API_KEY not found"
**Solution:** Add your API key to `.env` file:
```bash
echo "ANTHROPIC_API_KEY=your-actual-key-here" >> .env
```

### Issue: "Permission denied" on file upload
**Solution:** Check upload folder permissions:
```bash
chmod 755 uploads/
```

### Issue: Rate limit exceeded
**Solution:** Wait for rate limit to reset or restart application in development.

### Issue: CSRF token error
**Solution:** Ensure forms include `{{ form.hidden_tag() }}` and meta tag in base template.

## Production Readiness Checklist

Before deploying to production:

- [ ] Change all default passwords
- [ ] Set `FLASK_ENV=production`
- [ ] Use proper secret key (not in code)
- [ ] Enable HTTPS (set `SESSION_COOKIE_SECURE=True`)
- [ ] Configure proper CORS origins
- [ ] Set up proper database (PostgreSQL)
- [ ] Configure external storage (S3, etc.)
- [ ] Set up logging and monitoring
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up SSL certificates

## Development vs Production

| Feature | Development | Production |
|---------|-------------|------------|
| **Debug Mode** | Enabled | Disabled |
| **Secret Key** | Generated | Environment variable |
| **Database** | SQLite | PostgreSQL |
| **File Storage** | Local | Cloud (S3/GCS) |
| **HTTPS** | Optional | Required |
| **Rate Limiting** | Memory | Redis |
| **Error Pages** | Detailed | Generic |

## Next Steps

1. **Test thoroughly** with the secure version
2. **Customize authentication** (add password reset, etc.)
3. **Integrate with existing services** from services/ directory
4. **Add proper logging and monitoring**
5. **Prepare for cloud deployment**

## Security Contacts

If you discover security issues:
1. **Do not** create public GitHub issues
2. Report privately to system administrator
3. Include reproduction steps
4. Allow time for fix before disclosure

---

**Remember:** Security is an ongoing process. Regularly update dependencies and review security configurations.