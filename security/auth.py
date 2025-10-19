"""
Authentication Module
Handles user login, logout, and password management
"""

import streamlit as st
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# SIMPLE PASSWORD HASHING (using bcrypt is better, but this works for now)
def hash_password(password: str) -> str:
    """
    Convert password to a secure hash
    Like turning 'mypassword123' into gibberish that can't be reversed
    """
    # Add salt (random data) to make it more secure
    salt = secrets.token_hex(16)
    # Hash the password + salt
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # Number of iterations
    )
    # Return salt + hash (we need salt to verify later)
    return f"{salt}${password_hash.hex()}"


def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Check if provided password matches stored hash
    """
    try:
        # Split the stored password to get salt and hash
        salt, password_hash = stored_password.split('$')
        
        # Hash the provided password with the same salt
        provided_hash = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        
        # Compare the hashes
        return password_hash == provided_hash.hex()
    except:
        return False


class AuthManager:
    """
    Manages user authentication
    Think of this as the bouncer at a club - checks IDs and decides who gets in
    """
    
    def __init__(self):
        # Secret key for creating tokens (should be in environment variable)
        self.SECRET_KEY = st.secrets.get("JWT_SECRET_KEY", "CHANGE-THIS-SECRET-KEY-IN-PRODUCTION")
        
        # In a real app, users would be in a database
        # For now, we'll use a simple dictionary
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """
        Load user database
        In production, this would query a real database
        """
        # TEMPORARY: Hardcoded users (MUST CHANGE IN PRODUCTION)
        return {
            'admin': {
                'password_hash': hash_password('admin123'),  # ⚠️ CHANGE THIS
                'role': 'admin',
                'department': 'Management',
                'email': 'admin@psa.com'
            },
            'operations_user': {
                'password_hash': hash_password('ops123'),  # ⚠️ CHANGE THIS
                'role': 'user',
                'department': 'Operations',
                'email': 'ops@psa.com'
            },
            'viewer': {
                'password_hash': hash_password('view123'),  # ⚠️ CHANGE THIS
                'role': 'viewer',
                'department': 'Operations',
                'email': 'viewer@psa.com'
            }
        }
    
    def login(self, username: str, password: str) -> tuple[bool, str, Optional[Dict]]:
        """
        Attempt to log in a user
        
        Returns:
            (success, message, user_info)
        """
        # Check if user exists
        if username not in self.users:
            logger.warning(f"Failed login attempt for non-existent user: {username}")
            return False, "❌ Invalid username or password", None
        
        user = self.users[username]
        
        # Verify password
        if not verify_password(user['password_hash'], password):
            logger.warning(f"Failed login attempt for user: {username}")
            return False, "❌ Invalid username or password", None
        
        # Create session token
        token = self._create_token(username, user['role'], user['department'])
        
        # Store in session
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.user_role = user['role']
        st.session_state.user_department = user['department']
        st.session_state.auth_token = token
        st.session_state.login_time = datetime.now()
        
        logger.info(f"Successful login: {username}")
        return True, "✅ Login successful!", {
            'username': username,
            'role': user['role'],
            'department': user['department']
        }
    
    def logout(self):
        """
        Log out the current user
        """
        username = st.session_state.get('username', 'unknown')
        
        # Clear session
        for key in ['authenticated', 'username', 'user_role', 'user_department', 'auth_token', 'login_time']:
            if key in st.session_state:
                del st.session_state[key]
        
        logger.info(f"User logged out: {username}")
    
    def _create_token(self, username: str, role: str, department: str) -> str:
        """
        Create a JWT token
        Like a digital ticket that proves you're logged in
        """
        payload = {
            'username': username,
            'role': role,
            'department': department,
            'exp': datetime.utcnow() + timedelta(hours=8),  # Token expires in 8 hours
            'iat': datetime.utcnow()  # Issued at
        }
        
        return jwt.encode(payload, self.SECRET_KEY, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify a JWT token
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def is_authenticated(self) -> bool:
        """
        Check if current user is logged in
        """
        if not st.session_state.get('authenticated', False):
            return False
        
        # Check if token is still valid
        token = st.session_state.get('auth_token')
        if not token:
            return False
        
        payload = self.verify_token(token)
        return payload is not None
    
    def require_auth(self, allowed_roles: list = None):
        """
        Decorator-style function to protect pages
        Use this at the top of any page that requires login
        """
        if not self.is_authenticated():
            st.error("🔒 Please log in to access this page")
            st.stop()
        
        if allowed_roles:
            user_role = st.session_state.get('user_role')
            if user_role not in allowed_roles:
                st.error("⛔ You don't have permission to access this page")
                st.stop()
    
    def get_current_user(self) -> Optional[Dict]:
        """
        Get information about the current logged-in user
        """
        if not self.is_authenticated():
            return None
        
        return {
            'username': st.session_state.get('username'),
            'role': st.session_state.get('user_role'),
            'department': st.session_state.get('user_department')
        }


# Quick helper functions
def require_login():
    """
    Simple function to add at the top of protected pages
    """
    auth = AuthManager()
    auth.require_auth()


def require_role(allowed_roles: list):
    """
    Simple function to require specific roles
    Example: require_role(['admin', 'operations'])
    """
    auth = AuthManager()
    auth.require_auth(allowed_roles)