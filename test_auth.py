#!/usr/bin/env python3
"""
Test HTTP Basic Auth implementation
Run this to verify authentication is working before deploying
"""

import os
import requests
from requests.auth import HTTPBasicAuth

def test_auth():
    """Test authentication against local Flask app."""
    
    print("=" * 60)
    print("HTTP Basic Auth Test")
    print("=" * 60)
    print()
    
    # Check environment variables
    username = os.getenv('APP_USERNAME', 'admin')
    password = os.getenv('APP_PASSWORD', 'changeme')
    
    print(f"Testing with credentials:")
    print(f"  Username: {username}")
    print(f"  Password: {'*' * len(password)}")
    print()
    
    base_url = "http://localhost:5000"
    
    # Test 1: No authentication (should fail)
    print("Test 1: Accessing without credentials...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 401:
            print("  ✅ PASS: Got 401 Unauthorized (expected)")
        else:
            print(f"  ❌ FAIL: Got {response.status_code} (expected 401)")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    print()
    
    # Test 2: Wrong password (should fail)
    print("Test 2: Accessing with wrong password...")
    try:
        response = requests.get(
            base_url,
            auth=HTTPBasicAuth(username, 'wrongpassword'),
            timeout=5
        )
        if response.status_code == 401:
            print("  ✅ PASS: Got 401 Unauthorized (expected)")
        else:
            print(f"  ❌ FAIL: Got {response.status_code} (expected 401)")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    print()
    
    # Test 3: Correct credentials (should succeed)
    print("Test 3: Accessing with correct credentials...")
    try:
        response = requests.get(
            base_url,
            auth=HTTPBasicAuth(username, password),
            timeout=5
        )
        if response.status_code == 200:
            print("  ✅ PASS: Got 200 OK (expected)")
        else:
            print(f"  ❌ FAIL: Got {response.status_code} (expected 200)")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    print()
    
    # Test 4: Static files should be accessible
    print("Test 4: Accessing static file (should work without auth)...")
    try:
        response = requests.get(f"{base_url}/static/landing-bg.jpg", timeout=5)
        if response.status_code in [200, 304]:
            print("  ✅ PASS: Static file accessible")
        elif response.status_code == 404:
            print("  ⚠️  WARNING: Static file not found (might not exist yet)")
        else:
            print(f"  ❌ FAIL: Got {response.status_code}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    print()
    
    print("=" * 60)
    print("Test complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. If all tests passed, you're ready to deploy!")
    print("2. If tests failed, check your .env file")
    print("3. Make sure Flask app is running: python3 app.py")
    print()

if __name__ == '__main__':
    # Check if Flask app is running
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5000))
    sock.close()
    
    if result != 0:
        print("❌ ERROR: Flask app is not running on localhost:5000")
        print("Start it with: python3 app.py")
        print()
        exit(1)
    
    # Load environment variables from .env if present
    if os.path.exists('.env'):
        print("Loading environment variables from .env...")
        from dotenv import load_dotenv
        load_dotenv()
        print()
    
    test_auth()
