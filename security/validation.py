"""
Input Validation Module
Protects against malicious inputs
"""

import re
import html
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Validates and sanitizes user inputs
    Think of this as a security guard checking everything that comes into your app
    """
    
    # Dangerous patterns to look for
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # JavaScript
        r'javascript:',                 # JavaScript URLs
        r'on\w+\s*=',                  # Event handlers (onclick, onload, etc)
        r'<iframe',                     # Iframes
        r'<object',                     # Objects
        r'<embed',                      # Embeds
    ]
    
    @staticmethod
    def sanitize_html(input_string: str) -> str:
        """
        Clean HTML from user input to prevent XSS attacks
        
        Example:
            Input:  "<script>alert('hack')</script>Hello"
            Output: "&lt;script&gt;alert('hack')&lt;/script&gt;Hello"
        """
        if not input_string:
            return ""
        
        # Convert special HTML characters to safe versions
        sanitized = html.escape(input_string)
        
        # Log if dangerous content was found
        if input_string != sanitized:
            logger.warning(f"Potentially malicious input sanitized: {input_string[:50]}...")
        
        return sanitized
    
    @staticmethod
    def validate_imo(imo: str) -> tuple[bool, str]:
        """
        Validate IMO number format
        IMO numbers are 7 digits, sometimes with 'IMO' prefix
        
        Example valid: "1234567" or "IMO1234567"
        """
        if not imo:
            return False, "IMO number cannot be empty"
        
        # Remove spaces and convert to uppercase
        imo = imo.strip().upper()
        
        # Check format
        imo_pattern = r'^(IMO)?\d{7}$'
        if not re.match(imo_pattern, imo):
            return False, "Invalid IMO format. Must be 7 digits (e.g., 1234567 or IMO1234567)"
        
        # Remove IMO prefix if present
        imo_number = imo.replace('IMO', '')
        
        # Validate checksum (IMO numbers have a built-in validation)
        if not InputValidator._validate_imo_checksum(imo_number):
            return False, "Invalid IMO checksum"
        
        return True, imo_number
    
    @staticmethod
    def _validate_imo_checksum(imo: str) -> bool:
        """
        Validate IMO number checksum
        (IMO numbers have a mathematical check to ensure they're real)
        """
        if len(imo) != 7:
            return False
        
        try:
            # Calculate checksum
            total = sum(int(digit) * (7 - i) for i, digit in enumerate(imo[:6]))
            checksum = total % 10
            
            # Compare with last digit
            return checksum == int(imo[6])
        except:
            return False
    
    @staticmethod
    def validate_date_range(start_date, end_date) -> tuple[bool, str]:
        """
        Validate date range is reasonable
        """
        from datetime import datetime, timedelta
        
        if not start_date or not end_date:
            return False, "Both start and end dates are required"
        
        # Check end is after start
        if end_date < start_date:
            return False, "End date must be after start date"
        
        # Check range is not too large (prevent performance issues)
        max_days = 365
        if (end_date - start_date).days > max_days:
            return False, f"Date range cannot exceed {max_days} days"
        
        # Check dates are not in the future
        if end_date > datetime.now().date():
            return False, "End date cannot be in the future"
        
        return True, "Valid date range"
    
    @staticmethod
    def check_sql_injection(input_string: str) -> bool:
        """
        Check for SQL injection attempts
        Returns True if suspicious, False if safe
        """
        if not input_string:
            return False
        
        # Common SQL injection patterns
        sql_patterns = [
            r"('\s*(OR|AND)\s*'?\d+\s*'?='?\d+)",  # ' OR '1'='1
            r"(;|\-\-|\/\*|\*\/)",                  # SQL comments
            r"(DROP|DELETE|INSERT|UPDATE|EXEC|UNION)\s",  # SQL commands
        ]
        
        input_upper = input_string.upper()
        for pattern in sql_patterns:
            if re.search(pattern, input_upper, re.IGNORECASE):
                logger.critical(f"SQL injection attempt detected: {input_string[:50]}...")
                return True
        
        return False
    
    @staticmethod
    def validate_filename(filename: str) -> tuple[bool, str]:
        """
        Validate uploaded filename is safe
        """
        if not filename:
            return False, "Filename cannot be empty"
        
        # Check for directory traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            logger.warning(f"Directory traversal attempt: {filename}")
            return False, "Invalid filename"
        
        # Check file extension
        allowed_extensions = {'.pdf', '.csv', '.xlsx', '.txt', '.json'}
        extension = filename[filename.rfind('.'):].lower() if '.' in filename else ''
        
        if extension not in allowed_extensions:
            return False, f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
        
        return True, "Valid filename"


# Quick helper functions
def sanitize_html(text: str) -> str:
    """Quick sanitize function"""
    return InputValidator.sanitize_html(text)


def validate_imo(imo: str) -> tuple[bool, str]:
    """Quick IMO validation"""
    return InputValidator.validate_imo(imo)


def is_safe_input(text: str) -> bool:
    """
    Quick check if input is safe
    Returns True if safe, False if suspicious
    """
    if InputValidator.check_sql_injection(text):
        return False
    
    for pattern in InputValidator.DANGEROUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    
    return True