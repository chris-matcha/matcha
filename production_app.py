"""
Production-ready version of Matcha application
This wraps the main app with additional production configurations
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from app import app

# Production configurations
app.config['DEBUG'] = False
app.config['TESTING'] = False

# Ensure production secret key
if app.config['SECRET_KEY'] == 'your-secret-key-here-use-long-random-string':
    raise ValueError("Please set a secure SECRET_KEY in your environment variables!")

# Set up production logging
if not os.path.exists('logs'):
    os.mkdir('logs')

# Configure logging
file_handler = RotatingFileHandler(
    'logs/matcha.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)

file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))

file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Matcha application startup')

# Log startup information
app.logger.info(f'Flask environment: {os.environ.get("FLASK_ENV", "not set")}')
app.logger.info(f'Debug mode: {app.config["DEBUG"]}')
app.logger.info(f'Upload folder: {app.config["UPLOAD_FOLDER"]}')
app.logger.info(f'Output folder: {app.config["OUTPUT_FOLDER"]}')

# Additional production middleware can be added here
# For example: ProxyFix for running behind reverse proxy
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

if __name__ == '__main__':
    # This should not be used in production
    # Use gunicorn or another WSGI server instead
    print("WARNING: Using development server. Use a production WSGI server instead!")
    app.run()