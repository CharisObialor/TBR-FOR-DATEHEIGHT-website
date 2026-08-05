import os
os.environ['KORAPAY_SECRET_KEY'] = 'test_secret_key'
os.environ['KORAPAY_PUBLIC_KEY'] = 'test_public_key'

import sys
import asyncio

# Set up environment
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / '.env')

# Test imports
print('Testing imports...')

# Import the CAC verification endpoint
from server import api_router
from fastapi.testclient import TestClient

from fastapi import FastAPI

app = FastAPI()
app.include_router(api_router)

client = TestClient(app)

# Test the endpoint with minimal data
test_request = {
    'id': '00000011',
    'registration_type': 'RC',
    'registration_name': 'Test Business Limited',
    'verification_consent': True
}

print('Testing CAC verification endpoint...')
response = client.post('/api/cac/verify', json=test_request)
print(f'Status Code: {response.status_code}')
print(f'Response: {response.json()}')

# Test validation
from models import CACVerificationRequest, CACVerificationResponse
print('\nValidation test...')

# Test invalid registration type
invalid_request = {
    'id': '00000011',
    'registration_type': 'INVALID',
    'registration_name': 'Test Business Limited',
    'verification_consent': True
}

response2 = client.post('/api/cac/verify', json=invalid_request)
print(f'Invalid type - Status Code: {response2.status_code}')
print(f'Invalid type - Response: {response2.json()}')