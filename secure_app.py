"""
Secure version of Matcha application with authentication and security hardening
"""

import os
import secrets
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from dotenv import load_dotenv

# Import security modules
from auth import User
from forms import LoginForm, RegistrationForm, FileUploadForm
from security_config import (
    SecurityConfig, setup_security_headers, setup_csrf_protection, 
    setup_rate_limiting, require_auth, secure_file_upload,
    sanitize_input
)

# Load environment variables
load_dotenv()

# Initialize Flask app with security configuration
app = Flask(__name__)

# Security configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or SecurityConfig.generate_secret_key()
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour CSRF token validity
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session timeout

# File upload configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')
app.config['MAX_CONTENT_LENGTH'] = SecurityConfig.MAX_FILE_SIZE

# Create instance folder for database
app.instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(app.instance_path, exist_ok=True)

# Create upload/output directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Initialize security components
setup_security_headers(app)
csrf = setup_csrf_protection(app)
limiter = setup_rate_limiting(app)

# Configure CORS with security
CORS(app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(int(user_id))

# Initialize database
with app.app_context():
    User.init_db()

# API client setup (secure)
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print("WARNING: ANTHROPIC_API_KEY not found. Some features will be disabled.")

# Routes
@app.route('/')
def index():
    """Main dashboard - requires authentication"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """User login with rate limiting"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Sanitize input
        username = sanitize_input(form.username.data)
        password = form.password.data
        
        # Authenticate user
        user = User.get_user_by_username(username)
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=False)
            flash('Login successful!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def register():
    """User registration with rate limiting"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Sanitize input
        username = sanitize_input(form.username.data)
        email = sanitize_input(form.email.data)
        password = form.password.data
        
        # Create user
        user = User.create_user(username, email, password)
        if user:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html', user=current_user)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def upload():
    """Secure file upload with authentication and rate limiting"""
    form = FileUploadForm()
    
    if form.validate_on_submit():
        file = form.file.data
        adaptation_type = sanitize_input(form.adaptation_type.data)
        
        # Secure file upload
        filename, message = secure_file_upload(file, app.config['UPLOAD_FOLDER'])
        
        if filename:
            flash(f'File uploaded successfully: {filename}', 'success')
            # TODO: Process file with selected adaptation type
            return redirect(url_for('index'))
        else:
            flash(f'Upload failed: {message}', 'error')
    
    return render_template('upload.html', form=form)

@app.route('/api/status')
@login_required
@limiter.limit("30 per minute")
def api_status():
    """API status endpoint with authentication"""
    return jsonify({
        'status': 'ok',
        'user': current_user.username,
        'authenticated': True,
        'api_available': bool(api_key)
    })

@app.route('/health')
@limiter.limit("60 per minute")
def health_check():
    """Public health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0-secure'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(403)
def forbidden(error):
    return render_template('error.html', 
                         error_code=403, 
                         error_message="Access forbidden"), 403

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('error.html', 
                         error_code=429, 
                         error_message="Rate limit exceeded. Please try again later."), 429

@app.errorhandler(413)
def too_large(error):
    return render_template('error.html', 
                         error_code=413, 
                         error_message="File too large"), 413

# Context processor for templates
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

if __name__ == '__main__':
    # Development server configuration
    print("🍃 Starting Matcha Secure Application")
    print("📧 Default admin credentials: admin / admin123")
    print("⚠️  Remember to change default passwords!")
    print("🔒 Security features enabled:")
    print("   - Authentication required")
    print("   - CSRF protection")
    print("   - Rate limiting")
    print("   - Input sanitization")
    print("   - Secure file uploads")
    
    # Run with security warnings for development
    port = int(os.environ.get('PORT', 5001))  # Use PORT env var or default to 5001
    print(f"🌐 Server starting on http://127.0.0.1:{port}")
    app.run(
        debug=True,
        host='127.0.0.1',  # Localhost only
        port=port,
        threaded=True
    )