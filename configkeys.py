from dotenv import load_dotenv
import os
from pathlib import Path

# Load the .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Azure OpenAI Keys
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
DEPLOYMENT_ID = "gpt-4.1-mini"  # replace with your deployment ID

# Optional Power BI keys if you have them later
POWER_BI_CLIENT_ID = os.getenv("POWER_BI_CLIENT_ID")
POWER_BI_CLIENT_SECRET = os.getenv("POWER_BI_CLIENT_SECRET")

# Simple check
if not AZURE_OPENAI_API_KEY:
    raise ValueError("❌ Missing Azure OpenAI API key! Check your .env file.")
