# config.py
from dotenv import load_dotenv
import os
from pathlib import Path

# Load the .env file automatically from the project root
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Fetch all environment variables
POWER_BI_CLIENT_ID = os.getenv("POWER_BI_CLIENT_ID")
POWER_BI_CLIENT_SECRET = os.getenv("POWER_BI_CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
DATABASE_URL = os.getenv("DATABASE_URL")

# Optional: simple validation to make sure they exist
def check_env():
    missing = []
    for key, value in {
        "POWER_BI_CLIENT_ID": POWER_BI_CLIENT_ID,
        "POWER_BI_CLIENT_SECRET": POWER_BI_CLIENT_SECRET,
        "TENANT_ID": TENANT_ID,
        "DATABASE_URL": DATABASE_URL,
    }.items():
        if not value:
            missing.append(key)
    if missing:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

# Run validation when this file is imported
check_env()
