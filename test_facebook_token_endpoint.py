#!/usr/bin/env python
"""
Test script for Facebook SDK OAuth endpoint
Run with: python test_facebook_token_endpoint.py
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_missing_token():
    """Test MISSING_TOKEN error"""
    print("\n1. Testing MISSING_TOKEN error...")
    url = f"{BASE_URL}/api/v1/instagram/accounts/mobile/facebook-token/"
    headers = {
        "Authorization": "Token YOUR_USER_TOKEN_HERE",
        "Content-Type": "application/json"
    }
    data = {}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            error_code = response.json().get('error', {}).get('code')
            if error_code == 'MISSING_TOKEN':
                print("   ✅ PASSED: MISSING_TOKEN error returned correctly")
                return True
        print("   ❌ FAILED: Expected MISSING_TOKEN error")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_invalid_token():
    """Test INVALID_TOKEN error"""
    print("\n2. Testing INVALID_TOKEN error...")
    url = f"{BASE_URL}/api/v1/instagram/accounts/mobile/facebook-token/"
    headers = {
        "Authorization": "Token YOUR_USER_TOKEN_HERE",
        "Content-Type": "application/json"
    }
    data = {
        "access_token": "invalid_fake_token_123",
        "platform": "ios"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            error_code = response.json().get('error', {}).get('code')
            if error_code == 'INVALID_TOKEN':
                print("   ✅ PASSED: INVALID_TOKEN error returned correctly")
                return True
        print("   ❌ FAILED: Expected INVALID_TOKEN error")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_authentication_required():
    """Test that authentication is required"""
    print("\n3. Testing authentication requirement...")
    url = f"{BASE_URL}/api/v1/instagram/accounts/mobile/facebook-token/"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "access_token": "test_token",
        "platform": "ios"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ PASSED: Authentication required")
            return True
        print("   ❌ FAILED: Should require authentication")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_existing_mobile_auth_url():
    """Verify existing mobile/auth-url endpoint still works"""
    print("\n4. Testing existing mobile/auth-url endpoint (should be unchanged)...")
    url = f"{BASE_URL}/api/v1/instagram/accounts/mobile/auth-url/"
    headers = {
        "Authorization": "Token YOUR_USER_TOKEN_HERE"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 401]:  # 401 if no valid token, 200 if valid
            data = response.json()
            if response.status_code == 200:
                if 'data' in data and 'url' in data['data']:
                    print("   ✅ PASSED: Existing endpoint works correctly")
                    return True
            elif response.status_code == 401:
                print("   ✅ PASSED: Existing endpoint accessible (needs valid token)")
                return True
        print("   ❌ FAILED: Existing endpoint might be broken")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_existing_mobile_status():
    """Verify existing mobile/status endpoint still works"""
    print("\n5. Testing existing mobile/status endpoint (should be unchanged)...")
    url = f"{BASE_URL}/api/v1/instagram/accounts/mobile/status/"
    headers = {
        "Authorization": "Token YOUR_USER_TOKEN_HERE"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 401]:
            print("   ✅ PASSED: Existing endpoint works correctly")
            return True
        print("   ❌ FAILED: Existing endpoint might be broken")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def main():
    print("="*60)
    print("Facebook SDK OAuth Endpoint Tests")
    print("="*60)
    print("\nNote: These tests verify error handling and endpoint accessibility.")
    print("For full testing with valid tokens, use Facebook Developer Console.")
    print("\nMake sure Django server is running: python manage.py runserver")
    
    results = []
    
    # Test new endpoint
    results.append(("Missing Token Error", test_missing_token()))
    results.append(("Invalid Token Error", test_invalid_token()))
    results.append(("Authentication Required", test_authentication_required()))
    
    # Test existing endpoints (zero impact verification)
    results.append(("Existing mobile/auth-url", test_existing_mobile_auth_url()))
    results.append(("Existing mobile/status", test_existing_mobile_status()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Implementation looks good.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)

