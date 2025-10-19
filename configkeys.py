"""
Configuration Keys Module - SECURE VERSION
Now uses secure configuration management
"""

from config.secure_config import SecureConfig
import logging

logger = logging.getLogger(__name__)

# Create secure config instance
_config = SecureConfig()

# Get Azure OpenAI configuration securely
try:
    azure_config = _config.get_azure_openai_config()
    
    AZURE_OPENAI_ENDPOINT = azure_config['endpoint']
    AZURE_OPENAI_API_KEY = azure_config['api_key']
    AZURE_OPENAI_API_VERSION = azure_config['api_version']
    DEPLOYMENT_ID = azure_config['deployment_id']
    
    logger.info("✅ Azure OpenAI configuration loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load Azure OpenAI configuration: {e}")
    # Set to None so app can handle gracefully
    AZURE_OPENAI_ENDPOINT = None
    AZURE_OPENAI_API_KEY = None
    AZURE_OPENAI_API_VERSION = None
    DEPLOYMENT_ID = None

# Optional: Power BI configuration
try:
    POWER_BI_CLIENT_ID = _config.get_api_key('POWER_BI_CLIENT_ID')
    POWER_BI_CLIENT_SECRET = _config.get_api_key('POWER_BI_CLIENT_SECRET')
except:
    POWER_BI_CLIENT_ID = None
    POWER_BI_CLIENT_SECRET = None

# Optional: External API keys
try:
    MARINETRAFFIC_API_KEY = _config.get_api_key('MARINETRAFFIC_API_KEY')
except:
    MARINETRAFFIC_API_KEY = None

try:
    OPENWEATHER_API_KEY = _config.get_api_key('OPENWEATHER_API_KEY')
except:
    OPENWEATHER_API_KEY = None

# Validate required configuration
def validate_config():
    """Check if required configuration is present"""
    if not AZURE_OPENAI_API_KEY:
        return False, "❌ Azure OpenAI API key is missing"
    
    if not AZURE_OPENAI_ENDPOINT:
        return False, "❌ Azure OpenAI endpoint is missing"
    
    return True, "✅ Configuration is valid"