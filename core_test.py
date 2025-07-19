#!/usr/bin/env python3
"""
EdRina Resto Core Functionality Test
Focused test on critical backend functionality
"""

import requests
import json
import time

BASE_URL = "https://9aabc5f7-575f-4b4b-bbd7-48c6da06e7ea.preview.emergentagent.com/api"

def test_core_functionality():
    """Test core restaurant management functionality"""
    print("🔍 Testing Core EdRina Resto Functionality")
    print("=" * 50)
    
    # Test 1: System Initialization
    print("\n1. Testing System Initialization...")
    try:
        response = requests.post(f"{BASE_URL}/init", timeout=10)
        if response.status_code in [200, 201]:
            print("✅ System initialization successful")
            init_success = True
        else:
            print(f"❌ System initialization failed: {response.status_code}")
            init_success = False
    except Exception as e:
        print(f"❌ System initialization error: {e}")
        init_success = False
    
    # Test 2: Admin Login
    print("\n2. Testing Admin Login...")
    admin_token = None
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            admin_token = data.get("access_token")
            print(f"✅ Admin login successful: {data['user']['username']} ({data['user']['role']})")
            login_success = True
        else:
            print(f"❌ Admin login failed: {response.status_code} - {response.text}")
            login_success = False
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        login_success = False
    
    # Test 3: Menu Retrieval
    print("\n3. Testing Menu Retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/menu", timeout=10)
        if response.status_code == 200:
            menu_items = response.json()
            print(f"✅ Menu retrieved successfully: {len(menu_items)} items")
            print(f"   Sample items: {[item['name'] for item in menu_items[:3]]}")
            menu_success = True
        else:
            print(f"❌ Menu retrieval failed: {response.status_code}")
            menu_success = False
    except Exception as e:
        print(f"❌ Menu retrieval error: {e}")
        menu_success = False
    
    # Test 4: User Creation (if admin token available)
    user_creation_success = False
    if admin_token:
        print("\n4. Testing User Creation...")
        try:
            headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
            user_data = {"username": "test_serveur", "password": "test123", "role": "serveur"}
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                print("✅ User creation successful")
                user_creation_success = True
            else:
                print(f"❌ User creation failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ User creation error: {e}")
    
    # Test 5: Role-based Access Test
    print("\n5. Testing Role-based Access...")
    try:
        # Test server login
        login_data = {"username": "test_serveur", "password": "test123"}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            server_data = response.json()
            server_token = server_data.get("access_token")
            print(f"✅ Server login successful: {server_data['user']['role']}")
            
            # Test server trying to access admin endpoint
            headers = {"Authorization": f"Bearer {server_token}"}
            response = requests.get(f"{BASE_URL}/users", headers=headers, timeout=10)
            if response.status_code == 403:
                print("✅ Role-based access control working (server denied admin access)")
                rbac_success = True
            else:
                print(f"❌ Role-based access control failed: server got status {response.status_code}")
                rbac_success = False
        else:
            print(f"❌ Server login failed: {response.status_code}")
            rbac_success = False
    except Exception as e:
        print(f"❌ Role-based access test error: {e}")
        rbac_success = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CORE FUNCTIONALITY SUMMARY")
    print("=" * 50)
    
    tests = [
        ("System Initialization", init_success),
        ("Admin Authentication", login_success),
        ("Menu Management", menu_success),
        ("User Management", user_creation_success),
        ("Role-based Access Control", rbac_success)
    ]
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Success: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed >= 4:  # At least 4 out of 5 core functions working
        print("🟢 BACKEND CORE FUNCTIONALITY: WORKING")
        return True
    else:
        print("🔴 BACKEND CORE FUNCTIONALITY: ISSUES DETECTED")
        return False

if __name__ == "__main__":
    success = test_core_functionality()
    exit(0 if success else 1)