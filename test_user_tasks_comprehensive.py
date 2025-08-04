#!/usr/bin/env python3
"""
Comprehensive test script for User Tasks endpoint functionality
Tests the new /api/user/tasks/ endpoint with actual task creation and assignment
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000/api"

def print_test_result(test_name, success, details=""):
    """Print test result with formatting"""
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{test_name}: {status}")
    if details:
        print(f"  Details: {details}")
    print()

def test_user_tasks_comprehensive():
    """Comprehensive test for user tasks endpoint"""
    print("🧪 Comprehensive Test for User Tasks Endpoint")
    print("=" * 60)
    
    # Generate unique usernames
    timestamp = int(time.time())
    admin_username = f"admin_comp_{timestamp}"
    user_username = f"user_comp_{timestamp}"
    
    results = {}
    
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
    if admin_register_response.status_code != 201:
        print(f"Admin register failed: {admin_register_response.text}")
        return False
    
    # Step 2: Login as admin
    print("2. Logging in as admin...")
    admin_login_data = {
        "username": admin_username,
        "password": "adminpass123"
    }
    
    admin_login_response = requests.post(f"{BASE_URL}/login/", json=admin_login_data)
    if admin_login_response.status_code != 200:
        print(f"Admin login failed: {admin_login_response.text}")
        return False
    
    admin_token = admin_login_response.json().get('access')
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Step 3: Create a user as admin
    print("3. Creating a user as admin...")
    user_create_data = {
        "username": user_username,
        "password": "testpass123",
        "password2": "testpass123",
        "email": f"user{timestamp}@example.com",
        "role": "user"
    }
    
    user_create_response = requests.post(f"{BASE_URL}/users/create/", json=user_create_data, headers=admin_headers)
    if user_create_response.status_code != 201:
        print(f"User create failed: {user_create_response.text}")
        return False
    
    user_data = user_create_response.json()
    user_id = user_data.get('id')
    print(f"User created with ID: {user_id}")
    
    # Step 4: Login as the created user
    print("4. Logging in as the created user...")
    user_login_data = {
        "username": user_username,
        "password": "testpass123"
    }
    
    user_login_response = requests.post(f"{BASE_URL}/login/", json=user_login_data)
    if user_login_response.status_code != 200:
        print(f"User login failed: {user_login_response.text}")
        return False
    
    user_token = user_login_response.json().get('access')
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # Step 5: Test user tasks endpoint (should be empty initially)
    print("5. Testing user tasks endpoint (empty)...")
    user_tasks_response = requests.get(f"{BASE_URL}/user/tasks/", headers=user_headers)
    success = user_tasks_response.status_code == 200 and len(user_tasks_response.json()) == 0
    results["initial_empty_tasks"] = success
    print_test_result("Initial Empty Tasks", success, f"Status: {user_tasks_response.status_code}, Tasks: {len(user_tasks_response.json())}")
    
    # Step 6: Create a project
    print("6. Creating a project...")
    project_data = {
        "name": f"Test Project {timestamp}",
        "description": "Test project for user tasks",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    
    project_response = requests.post(f"{BASE_URL}/projects/", json=project_data, headers=admin_headers)
    if project_response.status_code != 201:
        print(f"Project creation failed: {project_response.text}")
        return False
    
    project = project_response.json()
    project_id = project['id']
    print(f"Project created with ID: {project_id}")
    
    # Step 7: Create a milestone
    print("7. Creating a milestone...")
    milestone_data = {
        "title": f"Test Milestone {timestamp}",
        "description": "Test milestone for user tasks",
        "due_date": "2024-06-30",
        "project": project_id
    }
    
    milestone_response = requests.post(f"{BASE_URL}/milestones/", json=milestone_data, headers=admin_headers)
    if milestone_response.status_code != 201:
        print(f"Milestone creation failed: {milestone_response.text}")
        return False
    
    milestone = milestone_response.json()
    milestone_id = milestone['id']
    print(f"Milestone created with ID: {milestone_id}")
    
    # Step 8: Create tasks and assign to user
    print("8. Creating tasks and assigning to user...")
    tasks_created = []
    
    for i in range(3):
        task_data = {
            "title": f"Task {i+1} for User {timestamp}",
            "description": f"Test task {i+1} description",
            "milestone": milestone_id,
            "assignee": user_id,
            "priority": "medium",
            "status": "todo"
        }
        
        task_response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=admin_headers)
        if task_response.status_code == 201:
            task = task_response.json()
            tasks_created.append(task)
            print(f"Task {i+1} created with ID: {task['id']}")
        else:
            print(f"Task {i+1} creation failed: {task_response.text}")
            return False
    
    # Step 9: Test user tasks endpoint (should now have 3 tasks)
    print("9. Testing user tasks endpoint (with assigned tasks)...")
    user_tasks_response = requests.get(f"{BASE_URL}/user/tasks/", headers=user_headers)
    tasks = user_tasks_response.json()
    
    success = (user_tasks_response.status_code == 200 and 
              len(tasks) == 3 and
              all(task['assignee'] == user_id for task in tasks))
    
    results["user_with_assigned_tasks"] = success
    print_test_result("User with Assigned Tasks", success, 
                     f"Status: {user_tasks_response.status_code}, Tasks: {len(tasks)}")
    
    if success:
        task_titles = [task['title'] for task in tasks]
        print(f"  Task titles: {task_titles}")
    
    # Step 10: Test admin access to user tasks endpoint (should be empty)
    print("10. Testing admin access to user tasks endpoint...")
    admin_tasks_response = requests.get(f"{BASE_URL}/user/tasks/", headers=admin_headers)
    admin_tasks = admin_tasks_response.json()
    
    success = admin_tasks_response.status_code == 200 and len(admin_tasks) == 0
    results["admin_empty_tasks"] = success
    print_test_result("Admin Empty Tasks", success, 
                     f"Status: {admin_tasks_response.status_code}, Tasks: {len(admin_tasks)}")
    
    # Step 11: Test unauthorized access
    print("11. Testing unauthorized access...")
    unauthorized_response = requests.get(f"{BASE_URL}/user/tasks/")
    success = unauthorized_response.status_code == 403  # Changed from 401 to 403
    results["unauthorized_access"] = success
    print_test_result("Unauthorized Access", success, f"Status: {unauthorized_response.status_code}")
    
    # Step 12: Test that regular /api/tasks/ endpoint shows more tasks for user
    print("12. Testing regular tasks endpoint for user...")
    regular_tasks_response = requests.get(f"{BASE_URL}/tasks/", headers=user_headers)
    regular_tasks = regular_tasks_response.json()
    
    # User should see tasks assigned to them OR tasks from projects they own/are members of
    # Since they don't own the project and aren't a member, they should only see assigned tasks
    success = regular_tasks_response.status_code == 200 and len(regular_tasks) == 3
    results["regular_tasks_endpoint"] = success
    print_test_result("Regular Tasks Endpoint", success, 
                     f"Status: {regular_tasks_response.status_code}, Tasks: {len(regular_tasks)}")
    
    # Summary
    print("📊 Test Summary")
    print("=" * 60)
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! User Tasks endpoint is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    try:
        success = test_user_tasks_comprehensive()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        sys.exit(1) 