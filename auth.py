# auth.py - User authentication and management
import bcrypt
import sqlite3
from datetime import datetime
from flask_login import UserMixin
from database import get_db

class User(UserMixin):
    """User class for Flask-Login"""
    def __init__(self, id, username, email=None):
        self.id = id
        self.username = username
        self.email = email

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_user(username, password, email=None):
    """Create a new user with hashed password"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return None, "Username already exists"
        
        # Hash password and create user
        password_hash = hash_password(password)
        created_at = datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO users (username, password_hash, email, created_at) VALUES (?, ?, ?, ?)",
            (username, password_hash, email, created_at)
        )
        db.commit()
        user_id = cursor.lastrowid
        db.close()
        
        return User(user_id, username, email), None
    except Exception as e:
        return None, str(e)

def get_user_by_username(username):
    """Get user by username"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, username, email FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        db.close()
        
        if row:
            return User(row['id'], row['username'], row['email'])
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def get_user_by_id(user_id):
    """Get user by ID (required for Flask-Login)"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        db.close()
        
        if row:
            return User(row['id'], row['username'], row['email'])
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def authenticate_user(username, password):
    """Authenticate user with username and password"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, username, email, password_hash FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row and verify_password(password, row['password_hash']):
            # Update last login
            cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", 
                         (datetime.now().isoformat(), row['id']))
            db.commit()
            db.close()
            return User(row['id'], row['username'], row['email'])
        
        db.close()
        return None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def change_password(user_id, old_password, new_password):
    """Change user password"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Verify old password
        cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row or not verify_password(old_password, row['password_hash']):
            db.close()
            return False, "Current password is incorrect"
        
        # Update to new password
        new_hash = hash_password(new_password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
        db.commit()
        db.close()
        
        return True, "Password changed successfully"
    except Exception as e:
        return False, str(e)

def get_user_count():
    """Get total number of users"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        count = cursor.fetchone()['count']
        db.close()
        return count
    except Exception as e:
        print(f"Error counting users: {e}")
        return 0
