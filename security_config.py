"""
Security configuration and utilities for Matcha application
"""

import os
import secrets
from functools import wraps
from flask import request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
import re


class SecurityConfig:
    """Security configuration class"""
    
    # File upload security
    ALLOWED_EXTENSIONS = {'.pdf', '.pptx', '.ppt'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER_PERMISSIONS = 0o755
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_UPLOAD = "10 per minute"
    RATELIMIT_LOGIN = "5 per minute"
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
    }
    
    @staticmethod
    def generate_secret_key():
        """Generate a secure secret key"""
        return secrets.token_hex(32)
    
    @staticmethod
    def is_safe_filename(filename):
        """Check if filename is safe"""
        if not filename or '..' in filename or '/' in filename or '\\' in filename:
            return False
        
        # Check for potentially dangerous extensions
        dangerous_extensions = {'.exe', '.bat', '.cmd', '.com', '.scr', '.js', '.vbs', '.jar'}
        file_ext = os.path.splitext(filename)[1].lower()
        
        return file_ext not in dangerous_extensions
    
    @staticmethod
    def validate_file_content(file_path, expected_type):
        """Basic file content validation"""
        try:
            file_size = os.path.getsize(file_path)
            if file_size > SecurityConfig.MAX_FILE_SIZE:
                return False, "File too large"
            
            if file_size == 0:
                return False, "Empty file"
            
            # Basic magic number checks
            with open(file_path, 'rb') as f:
                header = f.read(8)
            
            if expected_type == 'pdf' and not header.startswith(b'%PDF-'):
                return False, "Invalid PDF file"
            
            if expected_type in ['pptx', 'ppt'] and not header.startswith(b'PK'):
                return False, "Invalid PowerPoint file"
            
            return True, "Valid file"
            
        except Exception as e:
            return False, f"File validation error: {str(e)}"


def sanitize_input(input_string, max_length=1000):
    """Sanitize user input"""
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', str(input_string))
    
    # Limit length
    sanitized = sanitized[:max_length]
    
    # Remove leading/trailing whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def setup_security_headers(app):
    """Set up security headers for all responses"""
    
    @app.after_request
    def add_security_headers(response):
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response
    
    return app


def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if current_user.username != 'admin':  # Simple admin check
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def setup_csrf_protection(app):
    """Set up CSRF protection"""
    csrf = CSRFProtect()
    csrf.init_app(app)
    return csrf


def setup_rate_limiting(app):
    """Set up rate limiting"""
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[SecurityConfig.RATELIMIT_DEFAULT],
        storage_uri=SecurityConfig.RATELIMIT_STORAGE_URL
    )
    return limiter


def secure_file_upload(file, upload_folder):
    """Securely handle file upload"""
    if not file or not file.filename:
        return None, "No file provided"
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    if not filename:
        return None, "Invalid filename"
    
    # Check if file type is allowed
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in SecurityConfig.ALLOWED_EXTENSIONS:
        return None, f"File type {file_ext} not allowed"
    
    # Additional security checks
    if not SecurityConfig.is_safe_filename(filename):
        return None, "Filename contains unsafe characters"
    
    # Generate unique filename to prevent conflicts
    import uuid
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(upload_folder, unique_filename)
    
    try:
        # Save file
        file.save(file_path)
        
        # Validate file content
        expected_type = 'pdf' if file_ext == '.pdf' else 'pptx'
        is_valid, message = SecurityConfig.validate_file_content(file_path, expected_type)
        
        if not is_valid:
            os.remove(file_path)  # Clean up invalid file
            return None, message
        
        return unique_filename, "File uploaded successfully"
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return None, f"Upload failed: {str(e)}"