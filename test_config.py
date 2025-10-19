# test_config.py
import streamlit as st

print("=" * 50)
print("Testing Configuration Loading")
print("=" * 50)

# Test 1: Check if secrets are accessible
print("\n1. Checking Streamlit secrets...")
try:
    if hasattr(st, 'secrets'):
        print("   ✅ st.secrets exists")
        
        # List all keys in secrets
        if hasattr(st.secrets, '_secrets'):
            print(f"   📋 Available keys: {list(st.secrets._secrets.keys())}")
        
        # Try to access each key
        keys_to_check = [
            'ENCRYPTION_KEY',
            'JWT_SECRET_KEY',
            'AZURE_OPENAI_ENDPOINT',
            'AZURE_OPENAI_API_KEY',
            'AZURE_OPENAI_API_VERSION',
            'DEPLOYMENT_ID'
        ]
        
        for key in keys_to_check:
            try:
                value = st.secrets[key]
                # Only show first 10 chars for security
                preview = str(value)[:10] + "..." if len(str(value)) > 10 else str(value)
                print(f"   ✅ {key}: {preview}")
            except Exception as e:
                print(f"   ❌ {key}: Not found - {e}")
    else:
        print("   ❌ st.secrets not available")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Try loading secure config
print("\n2. Testing SecureConfig...")
try:
    from config.secure_config import SecureConfig
    config = SecureConfig()
    print("   ✅ SecureConfig imported successfully")
    
    # Try to get Azure config
    try:
        azure_config = config.get_azure_openai_config()
        print("   ✅ Azure config loaded:")
        print(f"      - Endpoint: {azure_config['endpoint'][:30]}...")
        print(f"      - API Key: {azure_config['api_key'][:10]}...")
        print(f"      - Version: {azure_config['api_version']}")
        print(f"      - Deployment: {azure_config['deployment_id']}")
    except Exception as e:
        print(f"   ❌ Failed to load Azure config: {e}")
        
except Exception as e:
    print(f"   ❌ Error importing SecureConfig: {e}")

# Test 3: Check configkeys.py
print("\n3. Testing configkeys.py...")
try:
    import configkeys
    print("   ✅ configkeys imported")
    
    if configkeys.AZURE_OPENAI_ENDPOINT:
        print(f"   ✅ ENDPOINT: {configkeys.AZURE_OPENAI_ENDPOINT[:30]}...")
    else:
        print("   ❌ ENDPOINT is None")
    
    if configkeys.AZURE_OPENAI_API_KEY:
        print(f"   ✅ API_KEY: {configkeys.AZURE_OPENAI_API_KEY[:10]}...")
    else:
        print("   ❌ API_KEY is None")
        
    if configkeys.AZURE_OPENAI_API_VERSION:
        print(f"   ✅ VERSION: {configkeys.AZURE_OPENAI_API_VERSION}")
    else:
        print("   ❌ VERSION is None")
        
    if configkeys.DEPLOYMENT_ID:
        print(f"   ✅ DEPLOYMENT: {configkeys.DEPLOYMENT_ID}")
    else:
        print("   ❌ DEPLOYMENT is None")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Test Complete!")
print("=" * 50)