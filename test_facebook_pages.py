#!/usr/bin/env python
"""
Quick test script to debug Facebook Pages API
Run this to test if the Facebook Pages API is working correctly
"""

import requests
import json

def test_user_info(access_token):
    """Test Facebook user info API"""
    
    print("👤 Testing Facebook User Info...")
    print("-" * 30)
    
    user_url = 'https://graph.facebook.com/v20.0/me'
    user_params = {
        'access_token': access_token,
        'fields': 'id,name,email'
    }
    
    try:
        response = requests.get(user_url, params=user_params)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            user_id = data.get('id', 'Unknown')
            user_name = data.get('name', 'Unknown')
            print(f"✅ User: {user_name} (ID: {user_id})")
            return user_id, user_name
        else:
            print(f"❌ User API Error: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None, None

def test_facebook_pages_api(access_token):
    """Test Facebook Pages API directly"""
    
    print("🔍 Testing Facebook Pages API...")
    print("=" * 50)
    
    # Test 1: Get user's Facebook Pages
    pages_url = 'https://graph.facebook.com/v20.0/me/accounts'
    pages_params = {
        'access_token': access_token,
        'fields': 'id,name,instagram_business_account'
    }
    
    try:
        print(f"📡 Calling: {pages_url}")
        print(f"📋 Params: {pages_params}")
        
        response = requests.get(pages_url, params=pages_params)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            
            if pages:
                print(f"\n✅ Found {len(pages)} Facebook Page(s):")
                for page in pages:
                    page_name = page.get('name', 'Unknown')
                    page_id = page.get('id', 'Unknown')
                    has_instagram = 'instagram_business_account' in page
                    
                    print(f"  📄 Page: {page_name} (ID: {page_id})")
                    print(f"  📱 Has Instagram: {has_instagram}")
                    
                    if has_instagram:
                        ig_account = page.get('instagram_business_account', {})
                        ig_id = ig_account.get('id', 'Unknown')
                        print(f"  🎯 Instagram Business ID: {ig_id}")
                        
                        # Test Instagram Business Account
                        test_instagram_account(access_token, ig_id)
                    else:
                        print(f"  ❌ No Instagram business account linked")
            else:
                print(f"\n❌ No Facebook Pages found")
                print(f"   This means either:")
                print(f"   - User doesn't manage any Facebook Pages")
                print(f"   - Missing 'pages_show_list' permission")
                print(f"   - Wrong Facebook account being used")
                print(f"   - App is in development mode without test users")
                print(f"   - User is not added as test user in Facebook app")
                
                # Test alternative endpoints
                test_alternative_endpoints(access_token)
        else:
            print(f"\n❌ API Error: {response.status_code}")
            error_data = response.json()
            print(f"   Error: {error_data}")
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")

def test_instagram_account(access_token, ig_business_id):
    """Test Instagram Business Account API"""
    
    print(f"\n🎯 Testing Instagram Business Account: {ig_business_id}")
    print("-" * 40)
    
    ig_url = f'https://graph.facebook.com/v20.0/{ig_business_id}'
    ig_params = {
        'access_token': access_token,
        'fields': 'id,username,account_type,media_count,followers_count,follows_count'
    }
    
    try:
        print(f"📡 Calling: {ig_url}")
        print(f"📋 Params: {ig_params}")
        
        response = requests.get(ig_url, params=ig_params)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            username = data.get('username', 'Unknown')
            account_type = data.get('account_type', 'Unknown')
            
            print(f"\n✅ Instagram Account Details:")
            print(f"  👤 Username: @{username}")
            print(f"  🏢 Account Type: {account_type}")
            print(f"  📊 Media Count: {data.get('media_count', 0)}")
            print(f"  👥 Followers: {data.get('followers_count', 0)}")
        else:
            print(f"\n❌ Instagram API Error: {response.status_code}")
            error_data = response.json()
            print(f"   Error: {error_data}")
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")

def test_alternative_endpoints(access_token):
    """Test alternative Facebook API endpoints"""
    
    print(f"\n🔄 Testing Alternative Endpoints...")
    print("-" * 40)
    
    # Test 1: Try with different fields
    print("📋 Test 1: Pages API with minimal fields")
    pages_url = 'https://graph.facebook.com/v20.0/me/accounts'
    pages_params = {
        'access_token': access_token,
        'fields': 'id,name'
    }
    
    try:
        response = requests.get(pages_url, params=pages_params)
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            print(f"📄 Found {len(pages)} pages with minimal fields")
            if pages:
                for page in pages:
                    print(f"  - {page.get('name', 'Unknown')} (ID: {page.get('id', 'Unknown')})")
        else:
            print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Try different API version
    print(f"\n📋 Test 2: Pages API with different version")
    pages_url_v18 = 'https://graph.facebook.com/v18.0/me/accounts'
    pages_params_v18 = {
        'access_token': access_token,
        'fields': 'id,name'
    }
    
    try:
        response = requests.get(pages_url_v18, params=pages_params_v18)
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            print(f"📄 Found {len(pages)} pages with v18 API")
            if pages:
                for page in pages:
                    print(f"  - {page.get('name', 'Unknown')} (ID: {page.get('id', 'Unknown')})")
        else:
            print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Check user permissions
    print(f"\n📋 Test 3: User permissions")
    permissions_url = 'https://graph.facebook.com/v20.0/me/permissions'
    permissions_params = {
        'access_token': access_token
    }
    
    try:
        response = requests.get(permissions_url, params=permissions_params)
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            permissions = data.get('data', [])
            print(f"📄 User permissions:")
            for perm in permissions:
                permission_name = perm.get('permission', 'Unknown')
                status = perm.get('status', 'Unknown')
                print(f"  - {permission_name}: {status}")
        else:
            print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main function"""
    
    print("🚀 Facebook Pages API Test Tool")
    print("=" * 50)
    print()
    print("This tool will help debug why the Facebook Pages API")
    print("is returning empty data for your Instagram connection.")
    print()
    
    # Get access token from user
    access_token = input("Enter your Facebook access token: ").strip()
    
    if not access_token:
        print("❌ No access token provided")
        return
    
    print()
    
    # Test user info first
    user_id, user_name = test_user_info(access_token)
    print()
    
    # Test Facebook Pages API
    test_facebook_pages_api(access_token)
    
    print("\n" + "=" * 50)
    print("🏁 Test Complete!")
    print()
    print("If you see 'No Facebook Pages found', check:")
    print("1. Facebook app permissions (pages_show_list)")
    print("2. Facebook account access to Pages")
    print("3. Instagram linking to Facebook Page")

if __name__ == "__main__":
    main()
