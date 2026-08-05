# CAC Verification API Integration Summary

## Overview
The Kakoku Backend has been successfully integrated with the Corporate Affairs Commission (CAC) verification API via Korapay's services. This implementation enables automated verification of Nigerian company registration numbers and business details.

## Implementation Details

### 1. **Models (models.py)**
Added CAC verification data models:
- `CACVerificationRequest`: Input model for CAC verification requests
  - `id`: Corporate Affairs Commission number (required)
  - `registration_type`: Registration type (RC, BN, IT, LP, LLP) (required)
  - `registration_name`: Business name (optional)
  - `verification_consent`: Consent flag for data verification (required)
- `CACVerificationResponse`: Response model from Korapay API
  - `success`: Verification result status
  - `message`: Human-readable message
  - `data`: Response data from Korapay
  - `error`: Error message if verification fails

### 2. **HTTP Client (server.py)**
Added a dedicated HTTP client for Korapay API:
- `get_Korapay_client()`: Singleton async HTTP client with connection pooling
- Base URL: `https://api.korapay.com/merchant/api/v1`
- Timeout: 15 seconds per request
- Connection limits: 20 keepalive connections, 100 total connections

### 3. **Environment Variables**
Configuration via `.env` file:
- `KORAPAY_SECRET_KEY`: Bearer token for API authentication (required)
- `KORAPAY_PUBLIC_KEY`: Optional public key for certain operations

### 4. **API Route (server.py)**
Created `/api/cac/verify` endpoint:
- **Method**: POST
- **Authentication**: Bearer token (`KORAPAY_SECRET_KEY`)
- **Request Body**: `CACVerificationRequest` object
- **Response**: `CACVerificationResponse` object
- **Features**:
  - Validation of `registration_type` against allowed values (RC, BN, IT, LP, LLP)
  - Sensitive data masking in logs (ID prefix display)
  - Comprehensive error handling for HTTP errors, request errors, and unexpected errors
  - Detailed logging for monitoring and debugging
  - Response format consistent with existing API patterns in the codebase

### 5. **Error Handling**
Robust error handling covering:
- Validation errors for invalid `registration_type`
- HTTP status errors (4xx, 5xx responses)
- Network/request errors
- Unexpected internal server errors
- Detailed error logging with full traceback for debugging

### 6. **Request Format**
Corresponds to Korapay API specification:
```json
{
  "id": "00000011",
  "registration_type": "RC",
  "registration_name": "Test Business Limited",
  "verification_consent": true
}
```

### 7. **Response Format**
Standardized response structure:
```json
{
  "success": true/false,
  "message": "Verification result description",
  "data": {"api_response_data"},
  "error": "Error message (if any)"
}
```

## Usage Example

### Python Client
```python
import httpx
import asyncio
from models import CACVerificationRequest
from fastapi.testclient import TestClient

async def verify_cac():
    # Test the API route
    from server import api_router
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(api_router)
    client = TestClient(app)
    
    request = CACVerificationRequest(
        id="00000011",
        registration_type="RC",
        registration_name="Test Business Limited",
        verification_consent=True
    )
    
    response = client.post("/api/cac/verify", json=request.dict())
    return response.json()

result = asyncio.run(verify_cac())
print(f"Verification Result: {result['success']}")
print(f"Message: {result['message']}")
```

## Testing
- Model validation works correctly
- Syntax validation passes for all modified files
- API route is properly defined and importable
- Error handling covers various failure scenarios
- Logging masks sensitive data appropriately

## Files Modified
1. `backend/models.py`: Added CACVerificationRequest and CACVerificationResponse
2. `backend/server.py`: Added get_Korapay_client() function, KORAPAY_SECRET_KEY/KORAPAY_PUBLIC_KEY env vars, and /api/cac/verify route

## Configuration Required
Add to your `.env` file:
```
KORAPAY_SECRET_KEY=your_actual_korapay_secret_key_here
KORAPAY_PUBLIC_KEY=your_actual_korapay_public_key_here (optional)
```

## Notes
- The integration uses the same async/await patterns as other API integrations in the codebase (e.g., Paystack)
- Error handling and logging are consistent with existing patterns
- Response models follow the same structure as other API responses in the backend
- Sensitive data is masked in logs to maintain security
- The API endpoint is accessible via `/api/cac/verify` and follows RESTful principles