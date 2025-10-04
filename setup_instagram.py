#!/usr/bin/env python
"""
Instagram OAuth Setup Script
Run this script to configure Instagram OAuth credentials
"""

import os
import sys
from pathlib import Path

def update_settings():
    """Update Django settings with Instagram credentials"""
    settings_file = Path(__file__).parent / 'config' / 'settings.py'
    
    print("🔧 Instagram OAuth Setup")
    print("=" * 50)
    print()
    print("To use Instagram OAuth, you need to:")
    print("1. Create an app at https://developers.facebook.com/")
    print("2. Add 'Instagram Basic Display' product")
    print("3. Get your Instagram App ID and Instagram App Secret")
    print()
    print("⚠️  IMPORTANT: Use Instagram App credentials, NOT Facebook App credentials!")
    print("   - Go to your app → Instagram Basic Display → Basic Display")
    print("   - Copy the 'Instagram App ID' and 'Instagram App Secret'")
    print()
    
    # Get credentials from user
    client_id = input("Enter your Instagram App ID (from Instagram Basic Display): ").strip()
    client_secret = input("Enter your Instagram App Secret (from Instagram Basic Display): ").strip()
    
    if not client_id or not client_secret:
        print("❌ Credentials cannot be empty!")
        return False
    
    # Read current settings
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Update credentials
    content = content.replace(
        "INSTAGRAM_CLIENT_ID = 'your_instagram_client_id_here'",
        f"INSTAGRAM_CLIENT_ID = '{client_id}'"
    )
    content = content.replace(
        "INSTAGRAM_CLIENT_SECRET = 'your_instagram_client_secret_here'",
        f"INSTAGRAM_CLIENT_SECRET = '{client_secret}'"
    )
    
    # Write updated settings
    with open(settings_file, 'w') as f:
        f.write(content)
    
    print()
    print("✅ Instagram credentials updated!")
    print()
    print("📋 Next steps:")
    print("1. In your Instagram app settings, add this redirect URI:")
    print("   http://localhost:8000/dashboard/instagram/callback/")
    print("2. Add test users in your Instagram app for development")
    print("3. Restart your Django server")
    print()
    print("📖 See INSTAGRAM_SETUP.md for detailed instructions")
    
    return True

if __name__ == "__main__":
    try:
        update_settings()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
