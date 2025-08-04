#!/usr/bin/env python3
"""
JWT Token Debug Script
This script helps debug JWT token validation issues
"""

import requests
import json

# API Base URL
BASE_URL = "http://localhost:8000/api"

def test_token_validation():
    """Test JWT token validation"""
    print("🔍 Testing JWT Token Validation")
    print(f"Base URL: {BASE_URL}")
    
    # Step 1: Register a new user
    print("\n1️⃣ Registering new user...")
    user_data = {
        "username": "debuguser",
        "email": "debug@example.com",
        "password": "debugpass123",
        "password2": "debugpass123",
        "first_name": "Debug",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/register/", json=user_data)
    print(f"Registration Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ User registered successfully")
    elif response.status_code == 400:
        print("⚠️ User might already exist, continuing...")
    else:
        print(f"❌ Registration failed: {response.text}")
        return
    
    # Step 2: Login to get token
    print("\n2️⃣ Logging in to get JWT token...")
    login_data = {
        "username": "debuguser",
        "password": "debugpass123"
    }
    
    response = requests.post(f"{BASE_URL}/login/", json=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        login_response = response.json()
        access_token = login_response.get("access")
        refresh_token = login_response.get("refresh")
        
        print("✅ Login successful!")
        print(f"Access Token: {access_token[:50]}...")
        print(f"Refresh Token: {refresh_token[:50]}...")
        
        # Step 3: Test token with a simple API call
        print("\n3️⃣ Testing token with /me/ endpoint...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/me/", headers=headers)
        print(f"Token Test Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Token is valid!")
            user_info = response.json()
            print(f"User Info: {user_info}")
        else:
            print(f"❌ Token validation failed: {response.text}")
            
        # Step 4: Test with milestone creation
        print("\n4️⃣ Testing token with milestone creation...")
        
        # First create a project
        project_data = {
            "name": "Debug Project",
            "description": "Project for debugging",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        response = requests.post(f"{BASE_URL}/projects/", json=project_data, headers=headers)
        print(f"Project Creation Status: {response.status_code}")
        
        if response.status_code == 201:
            project = response.json()
            project_id = project.get("id")
            print(f"✅ Project created with ID: {project_id}")
            
            # Now create a milestone
            milestone_data = {
                "title": "Debug Milestone",
                "due_date": "2024-06-30",
                "project": project_id
            }
            
            response = requests.post(f"{BASE_URL}/milestones/", json=milestone_data, headers=headers)
            print(f"Milestone Creation Status: {response.status_code}")
            
            if response.status_code == 201:
                milestone = response.json()
                print(f"✅ Milestone created successfully: {milestone}")
            else:
                print(f"❌ Milestone creation failed: {response.text}")
                print(f"Response Headers: {dict(response.headers)}")
        else:
            print(f"❌ Project creation failed: {response.text}")
            
    else:
        print(f"❌ Login failed: {response.text}")

if __name__ == "__main__":
    test_token_validation() 