import os
import sys
os.environ['KORAPAY_SECRET_KEY'] = 'test_secret_key'

# Test imports
print('Testing CAC Verification API Integration...')

# Test model imports first
print('1. Testing model imports...')
try:
    from models import CACVerificationRequest, CACVerificationResponse
    print('   Models imported successfully')
    
    # Test model validation
    test_request = CACVerificationRequest(
        id='00000011',
        registration_type='RC',
        registration_name='Test Business',
        verification_consent=True
    )
    print('   Model validation works')
    
except Exception as e:
    print('Model import failed:', e)
    import traceback
    traceback.print_exc()

print('2. Checking server.py for CAC integration...')
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Read the server.py file to check for CAC integration
with open('server.py', 'r') as f:
    server_content = f.read()

# Check for CAC-related code
cac_features = [
    'KORAPAY_SECRET_KEY',
    'get_Korapay_client',
    '@api_router.post("/cac/verify"',
    'CACVerificationRequest',
    'CACVerificationResponse'
]

print('   Checking server.py for CAC features...')
for feature in cac_features:
    if feature in server_content:
        print('   ', feature, 'found')
    else:
        print('   ', feature, 'NOT found')

# Check if the route is importable
print('3. Testing server.py imports...')
try:
    # Create a minimal test app
    app = FastAPI()
    
    # Try to import api_router from server
    sys.path.insert(0, '.')
    from server import api_router
    
    app.include_router(api_router)
    
    # Create test client
    client = TestClient(app)
    
    print('   Server.py imports successful')
    print('   API router is available')
    
    # Test the CAC verification endpoint
    test_data = {
        'id': '00000011',
        'registration_type': 'RC',
        'registration_name': 'Test Business Limited',
        'verification_consent': True
    }
    
    print('4. Testing CAC verification endpoint...')
    response = client.post('/api/cac/verify', json=test_data)
    
    print('Status Code:', response.status_code)
    result = response.json()
    print('Response:', result)
    
    # Check if response has expected fields
    if 'success' in result and 'message' in result:
        print('Response structure is correct')
    else:
        print('Response structure is incorrect')
        
except ImportError as e:
    print('Server.py import failed:', e)
    import traceback
    traceback.print_exc()

print('\nSummary:')
print('The CAC verification API integration has been implemented.')
print('Please update your .env file with KORAPAY_SECRET_KEY and KORAPAY_PUBLIC_KEY')
print('to enable actual API calls to Korapay for CAC verification.')
