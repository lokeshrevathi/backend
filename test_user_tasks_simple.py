#!/usr/bin/env python3
"""
Simple test script for User Tasks endpoint functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_user_tasks_simple():
    """Simple test for user tasks endpoint"""
    print("🧪 Simple Test for User Tasks Endpoint")
    print("=" * 50)
    
    # Generate unique usernames
    timestamp = int(time.time())
    admin_username = f"admin_tasks_{timestamp}"
    user_username = f"user_tasks_{timestamp}"
    
    # Step 1: Register as admin
    print("1. Registering as admin...")
    admin_register_data = {
        "username": admin_username,
        "password": "adminpass123",
        "password2": "adminpass123",
        "email": f"admin{timestamp}@example.com",
        "role": "admin"
    }
    
    admin_register_response = requests.post(f"{BASE_URL}/register/", json=admin_register_data)
    print(f"Admin register status: {admin_register_response.status_code}")
    
    if admin_register_response.status_code != 201:
        print(f"Admin register failed: {admin_register_response.text}")
        return False
    
    # Step 2: Login as admin
    print("2. Logging in as admin...")
    admin_login_data = {
        "username": "admin_test_tasks",
        "password": "adminpass123"
    }
    
    admin_login_response = requests.post(f"{BASE_URL}/login/", json=admin_login_data)
    print(f"Admin login status: {admin_login_response.status_code}")
    
    if admin_login_response.status_code != 200:
        print(f"Admin login failed: {admin_login_response.text}")
        return False
    
    admin_token = admin_login_response.json().get('access')
    print(f"Admin token received: {admin_token[:20]}...")
    
    # Step 3: Create a user as admin
    print("3. Creating a user as admin...")
    user_create_data = {
        "username": user_username,
        "password": "testpass123",
        "password2": "testpass123",
        "email": f"user{timestamp}@example.com",
        "role": "user"
    }
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_create_response = requests.post(f"{BASE_URL}/users/create/", json=user_create_data, headers=headers)
    print(f"User create status: {user_create_response.status_code}")
    
    if user_create_response.status_code != 201:
        print(f"User create failed: {user_create_response.text}")
        return False
    
    user_data = user_create_response.json()
    print(f"User created with ID: {user_data.get('id')}")
    
    # Step 4: Login as the created user
    print("4. Logging in as the created user...")
    user_login_data = {
        "username": user_username,
        "password": "testpass123"
    }
    
    user_login_response = requests.post(f"{BASE_URL}/login/", json=user_login_data)
    print(f"User login status: {user_login_response.status_code}")
    
    if user_login_response.status_code != 200:
        print(f"User login failed: {user_login_response.text}")
        return False
    
    user_token = user_login_response.json().get('access')
    print(f"User token received: {user_token[:20]}...")
    
    # Step 5: Test user tasks endpoint
    print("5. Testing user tasks endpoint...")
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    tasks_response = requests.get(f"{BASE_URL}/user/tasks/", headers=user_headers)
    print(f"User tasks status: {tasks_response.status_code}")
    
    if tasks_response.status_code == 200:
        tasks = tasks_response.json()
        print(f"Tasks found: {len(tasks)}")
        print(f"Response: {json.dumps(tasks, indent=2)}")
        
        # Step 6: Test that admin gets empty list too
        print("6. Testing admin access to user tasks endpoint...")
        admin_tasks_response = requests.get(f"{BASE_URL}/user/tasks/", headers=headers)
        print(f"Admin tasks status: {admin_tasks_response.status_code}")
        
        if admin_tasks_response.status_code == 200:
            admin_tasks = admin_tasks_response.json()
            print(f"Admin tasks found: {len(admin_tasks)}")
            print(f"Admin response: {json.dumps(admin_tasks, indent=2)}")
        
        return True
    else:
        print(f"User tasks failed: {tasks_response.text}")
        return False

if __name__ == "__main__":
    try:
        success = test_user_tasks_simple()
        if success:
            print("✅ Test passed!")
        else:
            print("❌ Test failed!")
    except Exception as e:
        print(f"❌ Exception: {e}") 