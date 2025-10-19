"""
Secure Configuration Module
Safely handles API keys and sensitive configuration
"""

import os
import streamlit as st
from security.encryption import DataEncryption
import logging

logger = logging.getLogger(__name__)


class SecureConfig:
    """
    Manages secure configuration and API keys
    Think of this as a vault for your secrets
    """
    
    def __init__(self):
        self.encryption = DataEncryption()
    
    def get_api_key(self, key_name: str) -> str:
        """
        Safely retrieve an API key
        
        Args:
            key_name: Name of the key (e.g., 'AZURE_OPENAI_API_KEY')
        
        Returns:
            The decrypted API key
        """
        # Try to get from Streamlit secrets first (best practice)
        if hasattr(st, 'secrets') and key_name in st.secrets:
            return st.secrets[key_name]
        
        # Try to get from environment variable
        env_value = os.getenv(key_name)
        if env_value:
            return env_value
        
        # Try to get encrypted version
        encrypted_key = os.getenv(f"{key_name}_ENCRYPTED")
        if encrypted_key:
            try:
                return self.encryption.decrypt(encrypted_key)
            except Exception as e:
                logger.error(f"Failed to decrypt {key_name}: {e}")
        
        # Not found
        logger.error(f"API key not found: {key_name}")
        raise ValueError(f"Missing API key: {key_name}")
    
    def get_azure_openai_config(self) -> dict:
        """
        Get Azure OpenAI configuration safely
        """
        try:
            return {
                'endpoint': self.get_api_key('AZURE_OPENAI_ENDPOINT'),
                'api_key': self.get_api_key('AZURE_OPENAI_API_KEY'),
                'api_version': self.get_api_key('AZURE_OPENAI_API_VERSION'),
                'deployment_id': os.getenv('DEPLOYMENT_ID', 'gpt-4.1-mini')
            }
        except ValueError as e:
            logger.error(f"Azure OpenAI configuration incomplete: {e}")
            st.error("⚠️ Azure OpenAI is not properly configured. Please contact administrator.")
            st.stop()
    
    def get_database_config(self) -> dict:
        """
        Get database configuration safely
        """
        try:
            return {
                'host': self.get_api_key('MYSQL_HOST'),
                'user': self.get_api_key('MYSQL_USER'),
                'password': self.get_api_key('MYSQL_PASSWORD'),
                'database': self.get_api_key('MYSQL_DATABASE'),
                'port': int(os.getenv('MYSQL_PORT', '3306'))
            }
        except ValueError as e:
            logger.warning(f"Database configuration incomplete: {e}")
            return None
    
    def check_all_keys(self) -> dict:
        """
        Check which required keys are configured
        Useful for diagnostics
        """
        required_keys = [
            'AZURE_OPENAI_ENDPOINT',
            'AZURE_OPENAI_API_KEY',
            'AZURE_OPENAI_API_VERSION',
        ]
        
        optional_keys = [
            'MYSQL_HOST',
            'MYSQL_USER',
            'MYSQL_PASSWORD',
            'MYSQL_DATABASE',
            'MARINETRAFFIC_API_KEY',
            'OPENWEATHER_API_KEY'
        ]
        
        status = {
            'required': {},
            'optional': {}
        }
        
        for key in required_keys:
            try:
                self.get_api_key(key)
                status['required'][key] = '✅ Configured'
            except:
                status['required'][key] = '❌ Missing'
        
        for key in optional_keys:
            try:
                self.get_api_key(key)
                status['optional'][key] = '✅ Configured'
            except:
                status['optional'][key] = '⚠️ Not configured'
        
        return status


# Global config instance
_secure_config = SecureConfig()

def get_api_key(key_name: str) -> str:
    """Quick function to get an API key"""
    return _secure_config.get_api_key(key_name)

def get_azure_config() -> dict:
    """Quick function to get Azure config"""
    return _secure_config.get_azure_openai_config()