"""
Session Management Module
Handles user sessions and timeouts
"""

import streamlit as st
from datetime import datetime, timedelta
import secrets
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages user sessions
    Think of this as tracking who's in the building and when they need to leave
    """
    
    # Configuration
    SESSION_TIMEOUT = timedelta(hours=8)      # Total session length
    IDLE_TIMEOUT = timedelta(minutes=30)      # Inactivity timeout
    
    def __init__(self):
        self._initialize_session()
    
    def _initialize_session(self):
        """Set up session tracking"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = secrets.token_hex(16)
        
        if 'session_created' not in st.session_state:
            st.session_state.session_created = datetime.now()
        
        if 'last_activity' not in st.session_state:
            st.session_state.last_activity = datetime.now()
    
    def update_activity(self):
        """
        Update last activity timestamp
        Call this on every page load
        """
        st.session_state.last_activity = datetime.now()
    
    def check_session_valid(self) -> tuple[bool, str]:
        """
        Check if current session is still valid
        
        Returns:
            (valid, reason_if_invalid)
        """
        if not st.session_state.get('authenticated', False):
            return False, "Not authenticated"
        
        now = datetime.now()
        
        # Check total session timeout
        session_created = st.session_state.get('session_created')
        if session_created:
            if now - session_created > self.SESSION_TIMEOUT:
                logger.info(f"Session expired (timeout): {st.session_state.get('username')}")
                return False, "Session expired. Please log in again."
        
        # Check idle timeout
        last_activity = st.session_state.get('last_activity')
        if last_activity:
            if now - last_activity > self.IDLE_TIMEOUT:
                logger.info(f"Session expired (idle): {st.session_state.get('username')}")
                return False, "Session expired due to inactivity. Please log in again."
        
        # Update activity
        self.update_activity()
        
        return True, "Valid"
    
    def destroy_session(self):
        """
        Destroy current session (logout)
        """
        # Clear all session data
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        logger.info("Session destroyed")
    
    def get_session_info(self) -> dict:
        """
        Get information about current session
        Useful for displaying to user
        """
        if not st.session_state.get('authenticated'):
            return None
        
        session_created = st.session_state.get('session_created')
        last_activity = st.session_state.get('last_activity')
        now = datetime.now()
        
        # Calculate time remaining
        time_since_creation = now - session_created if session_created else timedelta(0)
        time_since_activity = now - last_activity if last_activity else timedelta(0)
        
        session_remaining = self.SESSION_TIMEOUT - time_since_creation
        idle_remaining = self.IDLE_TIMEOUT - time_since_activity
        
        return {
            'username': st.session_state.get('username'),
            'logged_in_since': session_created,
            'last_activity': last_activity,
            'session_expires_in': str(session_remaining).split('.')[0],  # Remove microseconds
            'idle_expires_in': str(idle_remaining).split('.')[0],
            'session_id': st.session_state.get('session_id')
        }


# Global session manager
_session_manager = SessionManager()

def create_session():
    """Create a new session"""
    _session_manager._initialize_session()

def validate_session():
    """
    Validate current session
    Use this at the top of protected pages
    """
    valid, message = _session_manager.check_session_valid()
    
    if not valid:
        st.error(f"🔒 {message}")
        
        # Show login button
        if st.button("Go to Login"):
            st.session_state.show_login = True
            st.rerun()
        
        st.stop()
    
    return True

def destroy_session():
    """Destroy current session (logout)"""
    _session_manager.destroy_session()

def get_session_info():
    """Get current session information"""
    return _session_manager.get_session_info()