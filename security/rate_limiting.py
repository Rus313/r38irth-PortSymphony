"""
Rate Limiting Module
Prevents abuse by limiting request frequency
"""

import time
from collections import defaultdict
from datetime import datetime, timedelta
import streamlit as st
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Limits how many requests a user can make
    Think of this as a bouncer saying "slow down, buddy"
    """
    
    def __init__(self):
        # Store request timestamps for each user
        # In production, use Redis instead of memory
        self.requests = defaultdict(list)
        
        # Configuration
        self.MAX_REQUESTS_PER_MINUTE = 60
        self.MAX_REQUESTS_PER_HOUR = 1000
        self.CLEANUP_INTERVAL = 300  # Clean old data every 5 minutes
        self.last_cleanup = time.time()
    
    def check_rate_limit(self, user_id: str) -> tuple[bool, str]:
        """
        Check if user is within rate limits
        
        Returns:
            (allowed, message)
        """
        now = time.time()
        
        # Cleanup old data periodically
        if now - self.last_cleanup > self.CLEANUP_INTERVAL:
            self._cleanup_old_requests()
        
        # Get user's request history
        user_requests = self.requests[user_id]
        
        # Remove requests older than 1 hour
        cutoff_time = now - 3600  # 1 hour ago
        user_requests = [req_time for req_time in user_requests if req_time > cutoff_time]
        self.requests[user_id] = user_requests
        
        # Check hourly limit
        if len(user_requests) >= self.MAX_REQUESTS_PER_HOUR:
            logger.warning(f"Rate limit exceeded (hourly): {user_id}")
            return False, f"⏳ Too many requests. Limit: {self.MAX_REQUESTS_PER_HOUR}/hour. Try again in an hour."
        
        # Check per-minute limit
        minute_ago = now - 60
        recent_requests = [req_time for req_time in user_requests if req_time > minute_ago]
        
        if len(recent_requests) >= self.MAX_REQUESTS_PER_MINUTE:
            logger.warning(f"Rate limit exceeded (per minute): {user_id}")
            return False, f"⏳ Too many requests. Limit: {self.MAX_REQUESTS_PER_MINUTE}/minute. Please wait a moment."
        
        # Add this request
        self.requests[user_id].append(now)
        
        return True, "OK"
    
    def _cleanup_old_requests(self):
        """Remove old request data to free memory"""
        now = time.time()
        cutoff = now - 3600  # 1 hour ago
        
        # Remove old requests for each user
        for user_id in list(self.requests.keys()):
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if req_time > cutoff
            ]
            
            # Remove user entirely if no recent requests
            if not self.requests[user_id]:
                del self.requests[user_id]
        
        self.last_cleanup = now
        logger.debug("Rate limiter cleanup completed")
    
    def get_remaining_requests(self, user_id: str) -> dict:
        """
        Get how many requests user has remaining
        Useful for showing in UI
        """
        now = time.time()
        user_requests = self.requests.get(user_id, [])
        
        # Count recent requests
        hour_ago = now - 3600
        minute_ago = now - 60
        
        requests_last_hour = len([r for r in user_requests if r > hour_ago])
        requests_last_minute = len([r for r in user_requests if r > minute_ago])
        
        return {
            'remaining_per_hour': self.MAX_REQUESTS_PER_HOUR - requests_last_hour,
            'remaining_per_minute': self.MAX_REQUESTS_PER_MINUTE - requests_last_minute,
            'total_per_hour': self.MAX_REQUESTS_PER_HOUR,
            'total_per_minute': self.MAX_REQUESTS_PER_MINUTE
        }


# Global rate limiter instance
_rate_limiter = RateLimiter()

def check_rate_limit() -> bool:
    """
    Quick function to check rate limit for current user
    Returns True if allowed, False if blocked
    """
    # Get user ID (use session_state or IP address)
    user_id = st.session_state.get('username', 'anonymous')
    
    allowed, message = _rate_limiter.check_rate_limit(user_id)
    
    if not allowed:
        st.error(message)
        st.stop()
    
    return True