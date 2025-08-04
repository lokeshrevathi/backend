#!/usr/bin/env python3
"""
Test script to verify admin registration without authentication
and user/manager creation requiring admin authentication
"""

import requests
import json
import time

# API Base URL
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def print_response(response, title):
    """Print formatted API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    
    if response.status_code in [200, 201, 204]:
        print("✅ SUCCESS")
    else:
        print("❌ FAILED")

def test_public_user_registration():
    """Test public user registration (should fail)"""
    print("\n👤 Testing Public User Registration (Should Fail)")
    timestamp = int(time.time())
    user_data = {
        "username": f"publicuser{timestamp}",
        "email": f"public{timestamp}@example.com",
        "password": "testpass123",
        "password2": "testpass123",
        "first_name": "Public",
        "last_name": "User"
    }
    response = requests.post(f"{API_BASE}/register/", json=user_data)
    print_response(response, "Public User Registration")
    return response.status_code == 400  # Should fail

def test_public_admin_registration():
    """Test public admin registration (should work)"""
    print("\n👑 Testing Public Admin Registration")
    timestamp = int(time.time())
    admin_data = {
        "username": f"publicadmin{timestamp}",
        "email": f"publicadmin{timestamp}@example.com",
        "password": "testpass123",
        "password2": "testpass123",
        "first_name": "Public",
        "last_name": "Admin",
        "role": "admin"
    }
    response = requests.post(f"{API_BASE}/register/", json=admin_data)
    print_response(response, "Public Admin Registration")
    return response.status_code == 201, admin_data["username"], "testpass123"

def test_public_manager_registration():
    """Test public manager registration (should fail)"""
    print("\n👔 Testing Public Manager Registration (Should Fail)")
    timestamp = int(time.time())
    manager_data = {
        "username": f"publicmanager{timestamp}",
        "email": f"publicmanager{timestamp}@example.com",
        "password": "testpass123",
        "password2": "testpass123",
        "first_name": "Public",
        "last_name": "Manager",
        "role": "manager"
    }
    response = requests.post(f"{API_BASE}/register/", json=manager_data)
    print_response(response, "Public Manager Registration")
    return response.status_code == 400  # Should fail

def test_admin_login(username, password):
    """Test admin login"""
    print(f"\n🔐 Testing Admin Login for {username}")
    login_data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{API_BASE}/login/", json=login_data)
    print_response(response, "Admin Login")
    if response.status_code == 200:
        return response.json().get("access")
    return None

def test_admin_creates_manager(token):
    """Test admin creating a manager (should work)"""
    print("\n👔 Testing Admin Creates Manager")
    headers = {"Authorization": f"Bearer {token}"}
    timestamp = int(time.time())
    manager_data = {
        "username": f"manager{timestamp}",
        "email": f"manager{timestamp}@example.com",
        "password": "testpass123",
        "password2": "testpass123",
        "first_name": "Manager",
        "last_name": "User",
        "role": "manager"
    }
    response = requests.post(f"{API_BASE}/users/create/", json=manager_data, headers=headers)
    print_response(response, "Admin Creates Manager")
    return response.status_code == 201

def test_admin_creates_user(token):
    """Test admin creating a regular user (should work)"""
    print("\n👤 Testing Admin Creates User")
    headers = {"Authorization": f"Bearer {token}"}
    timestamp = int(time.time())
    user_data = {
        "username": f"user{timestamp}",
        "email": f"user{timestamp}@example.com",
        "password": "testpass123",
        "password2": "testpass123",
        "first_name": "Regular",
        "last_name": "User",
        "role": "user"
    }
    response = requests.post(f"{API_BASE}/users/create/", json=user_data, headers=headers)
    print_response(response, "Admin Creates User")
    return response.status_code == 201

def test_admin_creates_admin(token):
    """Test admin creating another admin (should work)"""
    print("\n👑 Testing Admin Creates Another Admin")
    headers = {"Authorization": f"Bearer {token}"}
    timestamp = int(time.time())
    admin_data = {
        "username": f"admin2{timestamp}",
        "email": f"admin2{timestamp}@example.com",
        "password": "testpass123",
        "password2": "testpass123",
        "first_name": "Second",
        "last_name": "Admin",
        "role": "admin"
    }
    response = requests.post(f"{API_BASE}/users/create/", json=admin_data, headers=headers)
    print_response(response, "Admin Creates Another Admin")
    return response.status_code == 201

def test_unauthorized_user_creation():
    """Test unauthorized user trying to create users (should fail)"""
    print("\n🚫 Testing Unauthorized User Creation (Should Fail)")
    # Try to create a user without authentication
    timestamp = int(time.time())
    user_data = {
        "username": f"unauthorized{timestamp}",
        "email": f"unauthorized{timestamp}@example.com",
        "password": "testpass123",
        "password2": "testpass123",
        "first_name": "Unauthorized",
        "last_name": "User",
        "role": "user"
    }
    response = requests.post(f"{API_BASE}/users/create/", json=user_data)
    print_response(response, "Unauthorized User Creation")
    return response.status_code == 401  # Should fail

def main():
    """Main test function"""
    print("🚀 Testing Admin Registration and User/Manager Creation Rules")
    print(f"Base URL: {BASE_URL}")
    print(f"API Base: {API_BASE}")
    
    results = {}
    
    # Test 1: Public user registration (should fail)
    results["public_user_registration"] = test_public_user_registration()
    
    # Test 2: Public admin registration (should work)
    admin_success, admin_username, admin_password = test_public_admin_registration()
    results["public_admin_registration"] = admin_success
    
    # Test 3: Public manager registration (should fail)
    results["public_manager_registration"] = test_public_manager_registration()
    
    # Test 4: Admin login
    admin_token = test_admin_login(admin_username, admin_password)
    results["admin_login"] = admin_token is not None
    
    if admin_token:
        # Test 5: Admin creates manager (should work)
        results["admin_creates_manager"] = test_admin_creates_manager(admin_token)
        
        # Test 6: Admin creates user (should work)
        results["admin_creates_user"] = test_admin_creates_user(admin_token)
        
        # Test 7: Admin creates another admin (should work)
        results["admin_creates_admin"] = test_admin_creates_admin(admin_token)
    
    # Test 8: Unauthorized user creation (should fail)
    results["unauthorized_user_creation"] = test_unauthorized_user_creation()
    
    # Print Summary
    print("\n" + "="*80)
    print("📊 ADMIN REGISTRATION TEST RESULTS")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n📋 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print("\n📋 Expected Behavior:")
    print("❌ Public registration should NOT allow 'user' role")
    print("✅ Public registration should allow 'admin' role")
    print("❌ Public registration should NOT allow 'manager' role")
    print("✅ Admin should be able to create users via /api/users/create/")
    print("✅ Admin should be able to create managers via /api/users/create/")
    print("✅ Admin should be able to create admins via /api/users/create/")
    print("❌ Unauthorized users should NOT be able to create users")
    
    if failed_tests == 0:
        print("\n🎉 All admin registration rules are working correctly!")
    else:
        print(f"\n⚠️  {failed_tests} test(s) need attention.")
    
    return results

if __name__ == "__main__":
    main() 