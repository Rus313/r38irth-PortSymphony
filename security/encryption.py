"""
Encryption Module
Protects sensitive data
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import streamlit as st
import logging

logger = logging.getLogger(__name__)


class DataEncryption:
    """
    Handles encryption and decryption of sensitive data
    Think of this as a safe that locks up your valuables
    """
    
    def __init__(self):
        # Get or create encryption key
        self.key = self._get_encryption_key()
        self.cipher = Fernet(self.key)
    
    def _get_encryption_key(self) -> bytes:
        """
        Get encryption key from environment or generate one
        """
        # Try to get from Streamlit secrets
        if hasattr(st, 'secrets') and 'ENCRYPTION_KEY' in st.secrets:
            key_string = st.secrets['ENCRYPTION_KEY']
            return base64.urlsafe_b64decode(key_string.encode())
        
        # Try to get from environment variable
        key_env = os.getenv('ENCRYPTION_KEY')
        if key_env:
            return base64.urlsafe_b64decode(key_env.encode())
        
        # Generate a new key (WARNING: This will change on restart!)
        logger.warning("No encryption key found. Generating new key (will change on restart!)")
        return Fernet.generate_key()
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt a string
        
        Example:
            Input:  "my_api_key_12345"
            Output: "gAAAAABh..."  (gibberish)
        """
        if not data:
            return ""
        
        try:
            # Convert string to bytes, encrypt, then convert back to string
            encrypted_bytes = self.cipher.encrypt(data.encode())
            encrypted_string = base64.urlsafe_b64encode(encrypted_bytes).decode()
            return encrypted_string
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt a string
        
        Example:
            Input:  "gAAAAABh..."  (gibberish)
            Output: "my_api_key_12345"
        """
        if not encrypted_data:
            return ""
        
        try:
            # Convert string to bytes, decrypt, then convert back to string
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise


# Quick helper functions
_encryptor = DataEncryption()

def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key"""
    return _encryptor.encrypt(api_key)

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key"""
    return _encryptor.decrypt(encrypted_key)