#!/usr/bin/env python
"""
Quick test script for Hosted API endpoints
Run: python test_hosted_api.py
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"

def test_auth():
    """Test authentication endpoint"""
    print("\n=== Testing POST /api/auth ===")
    
    url = f"{BASE_URL}/api/auth"
    payload = {"email": TEST_EMAIL}
    
    print(f"Request: POST {url}")
    print(f"Body: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Authentication successful")
            return data.get('authToken')
        else:
            print("✗ Authentication failed")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def test_ai(auth_token):
    """Test AI proxy endpoint"""
    print("\n=== Testing POST /api/ai ===")
    
    if not auth_token:
        print("✗ Skipping AI test - no auth token")
        return
    
    url = f"{BASE_URL}/api/ai"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": "Say hello in one sentence",
        "userEmail": TEST_EMAIL,
        "options": {
            "model": "gpt-4o-mini",
            "maxTokens": 100
        }
    }
    
    print(f"Request: POST {url}")
    print(f"Headers: Authorization: Bearer {auth_token[:20]}...")
    print(f"Body: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ AI request successful")
            return True
        else:
            print("✗ AI request failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("Hosted API Test Script")
    print("=" * 60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    
    # Test authentication
    auth_token = test_auth()
    
    if not auth_token:
        print("\n✗ Tests failed - authentication not working")
        sys.exit(1)
    
    # Test AI endpoint
    ai_success = test_ai(auth_token)
    
    print("\n" + "=" * 60)
    if ai_success:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)

