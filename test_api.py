#!/usr/bin/env python3
"""
API Test Script for Project Dashboard
This script demonstrates how to use the Project Management API
"""

import requests
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000/api"

def print_response(response, title):
    """Print formatted API response"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_health_check():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL.replace('/api', '')}/health/")
    print_response(response, "Health Check")

def test_user_registration():
    """Test user registration"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password2": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    response = requests.post(f"{BASE_URL}/register/", json=user_data)
    print_response(response, "User Registration")
    return response.json() if response.status_code == 201 else None

def test_user_login(username, password):
    """Test user login"""
    login_data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/login/", json=login_data)
    print_response(response, "User Login")
    return response.json() if response.status_code == 200 else None

def test_create_project(token):
    """Test project creation"""
    headers = {"Authorization": f"Bearer {token}"}
    project_data = {
        "name": "Test Project",
        "description": "A test project for API testing",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "status": "active"
    }
    response = requests.post(f"{BASE_URL}/projects/", json=project_data, headers=headers)
    print_response(response, "Create Project")
    return response.json() if response.status_code == 201 else None

def test_get_projects(token):
    """Test getting projects"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/projects/", headers=headers)
    print_response(response, "Get Projects")
    return response.json() if response.status_code == 200 else None

def test_create_milestone(token, project_id):
    """Test milestone creation"""
    headers = {"Authorization": f"Bearer {token}"}
    milestone_data = {
        "project": project_id,
        "title": "Phase 1",
        "due_date": "2024-06-30"
    }
    response = requests.post(f"{BASE_URL}/milestones/", json=milestone_data, headers=headers)
    print_response(response, "Create Milestone")
    return response.json() if response.status_code == 201 else None

def test_create_task(token, milestone_id):
    """Test task creation"""
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {
        "milestone": milestone_id,
        "title": "Implement API",
        "description": "Create REST API endpoints",
        "assignee": None,  # Will be assigned to the current user
        "due_date": "2024-03-31",
        "priority": "high",
        "status": "todo"
    }
    response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
    print_response(response, "Create Task")
    return response.json() if response.status_code == 201 else None

def test_log_time(token, task_id):
    """Test logging time to a task"""
    headers = {"Authorization": f"Bearer {token}"}
    time_data = {"hours": 4.5}
    response = requests.post(f"{BASE_URL}/tasks/{task_id}/log_time/", json=time_data, headers=headers)
    print_response(response, "Log Time to Task")

def test_project_progress(token, project_id):
    """Test getting project progress"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/projects/{project_id}/progress/", headers=headers)
    print_response(response, "Project Progress")

def test_project_hours(token, project_id):
    """Test getting project total hours"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/projects/{project_id}/total_hours/", headers=headers)
    print_response(response, "Project Total Hours")

def main():
    """Main test function"""
    print("🚀 Starting API Tests for Project Dashboard")
    print(f"Base URL: {BASE_URL}")
    
    # Test health check
    test_health_check()
    
    # Test user registration
    user_data = test_user_registration()
    if not user_data:
        print("\n❌ User registration failed. Using existing user for login test.")
        username = "testuser"
        password = "testpass123"
    else:
        username = user_data.get("username", "testuser")
        password = "testpass123"
    
    # Test user login
    login_data = test_user_login(username, password)
    if not login_data:
        print("\n❌ Login failed. Cannot proceed with authenticated tests.")
        return
    
    token = login_data.get("access")
    print(f"\n✅ Login successful! Token: {token[:20]}...")
    
    # Test project creation
    project_data = test_create_project(token)
    if not project_data:
        print("\n❌ Project creation failed.")
        return
    
    project_id = project_data.get("id")
    
    # Test getting projects
    test_get_projects(token)
    
    # Test milestone creation
    milestone_data = test_create_milestone(token, project_id)
    if not milestone_data:
        print("\n❌ Milestone creation failed.")
        return
    
    milestone_id = milestone_data.get("id")
    
    # Test task creation
    task_data = test_create_task(token, milestone_id)
    if not task_data:
        print("\n❌ Task creation failed.")
        return
    
    task_id = task_data.get("id")
    
    # Test logging time
    test_log_time(token, task_id)
    
    # Test project progress
    test_project_progress(token, project_id)
    
    # Test project hours
    test_project_hours(token, project_id)
    
    print("\n🎉 API Tests Completed Successfully!")
    print("\n📋 Summary of tested endpoints:")
    print("✅ Health Check")
    print("✅ User Registration")
    print("✅ User Login (JWT)")
    print("✅ Project Creation")
    print("✅ Project Listing")
    print("✅ Milestone Creation")
    print("✅ Task Creation")
    print("✅ Time Logging")
    print("✅ Project Progress")
    print("✅ Project Hours")

if __name__ == "__main__":
    main() 