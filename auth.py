"""
Authentication module for Matcha application
Provides user management, login/logout, and security features
"""

import os
import sqlite3
from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt


class User(UserMixin):
    def __init__(self, id, username, email, password_hash, created_at, is_active=True):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        # Convert created_at string to datetime object if it's a string
        if isinstance(created_at, str):
            try:
                self.created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                # Fallback for different date formats
                try:
                    self.created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
                except (ValueError, AttributeError):
                    try:
                        self.created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    except (ValueError, AttributeError):
                        self.created_at = datetime.now()
        else:
            self.created_at = created_at or datetime.now()
        self._is_active = is_active
    
    @property
    def is_active(self):
        """Flask-Login requires this property"""
        return self._is_active

    def check_password(self, password):
        """Check if provided password matches stored hash"""
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        db_path = os.path.join(current_app.instance_path, 'matcha.db')
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, email, password_hash, created_at, is_active FROM users WHERE id = ?",
                    (user_id,)
                )
                result = cursor.fetchone()
                if result:
                    return User(*result)
        except sqlite3.Error:
            return None
        return None

    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        db_path = os.path.join(current_app.instance_path, 'matcha.db')
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, email, password_hash, created_at, is_active FROM users WHERE username = ?",
                    (username,)
                )
                result = cursor.fetchone()
                if result:
                    return User(*result)
        except sqlite3.Error:
            return None
        return None

    @staticmethod
    def create_user(username, email, password):
        """Create new user"""
        db_path = os.path.join(current_app.instance_path, 'matcha.db')
        password_hash = generate_password_hash(password)
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, created_at, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, email, password_hash, datetime.utcnow(), True))
                
                user_id = cursor.lastrowid
                return User.get_user_by_id(user_id)
        except sqlite3.Error:
            return None

    @staticmethod
    def init_db():
        """Initialize user database"""
        db_path = os.path.join(current_app.instance_path, 'matcha.db')
        os.makedirs(current_app.instance_path, exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Create sessions table for additional security
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create default admin user if none exists
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                # Generate a secure default password - CHANGE THIS IN PRODUCTION!
                import secrets
                default_password = secrets.token_urlsafe(16)
                admin_password = generate_password_hash(default_password)
                print(f"Default admin password: {default_password}")
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, created_at, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, ('admin', 'admin@matcha.local', admin_password, datetime.utcnow(), True))
            
            conn.commit()


def create_demo_user():
    """Create a demo user for testing"""
    return User.create_user('demo', 'demo@matcha.local', 'demo123')