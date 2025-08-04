#!/usr/bin/env python3
"""
Test script for User Tasks endpoint functionality
Tests the new /api/user/tasks/ endpoint with role constraints
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def print_test_result(test_name, success, details=""):
    """Print test result with formatting"""
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{test_name}: {status}")
    if details:
        print(f"  Details: {details}")
    print()

def register_user(username, password, email, role='user'):
    """Register a new user"""
    url = f"{BASE_URL}/register/"
    data = {
        "username": username,
        "password": password,
        "password2": password,
        "email": email,
        "role": role
    }
    
    response = requests.post(url, json=data)
    return response

def login_user(username, password):
    """Login user and return token"""
    url = f"{BASE_URL}/login/"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json().get('access')
    return None

def create_project(token, name, description, start_date, end_date):
    """Create a project"""
    url = f"{BASE_URL}/projects/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": name,
        "description": description,
        "start_date": start_date,
        "end_date": end_date
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        return response.json()
    return None

def create_milestone(token, title, description, due_date, project_id):
    """Create a milestone"""
    url = f"{BASE_URL}/milestones/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": title,
        "description": description,
        "due_date": due_date,
        "project": project_id
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        return response.json()
    return None

def create_task(token, title, description, milestone_id, assignee_id=None, priority='medium', status='todo'):
    """Create a task"""
    url = f"{BASE_URL}/tasks/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": title,
        "description": description,
        "milestone": milestone_id,
        "priority": priority,
        "status": status
    }
    if assignee_id:
        data["assignee"] = assignee_id
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        return response.json()
    return None

def get_user_tasks(token):
    """Get tasks for the authenticated user"""
    url = f"{BASE_URL}/user/tasks/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    return response

def test_user_tasks_endpoint():
    """Test the user tasks endpoint with role constraints"""
    print("🧪 Testing User Tasks Endpoint with Role Constraints")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Register and login as admin
    print("1. Testing Admin Access to User Tasks Endpoint")
    admin_response = register_user("admin_test_user_tasks", "adminpass123", "admin@test.com", "admin")
    if admin_response.status_code == 201:
        admin_token = login_user("admin_test_user_tasks", "adminpass123")
        if admin_token:
            admin_tasks_response = get_user_tasks(admin_token)
            # Admin should get empty list (no tasks assigned to them)
            success = admin_tasks_response.status_code == 200 and len(admin_tasks_response.json()) == 0
            results["admin_access"] = success
            print_test_result("Admin Access", success, f"Status: {admin_tasks_response.status_code}, Tasks: {len(admin_tasks_response.json())}")
        else:
            results["admin_access"] = False
            print_test_result("Admin Access", False, "Failed to login admin")
    else:
        results["admin_access"] = False
        print_test_result("Admin Access", False, f"Failed to register admin: {admin_response.status_code}")
    
    # Test 2: Register and login as manager
    print("2. Testing Manager Access to User Tasks Endpoint")
    manager_response = register_user("manager_test_user_tasks", "managerpass123", "manager@test.com", "manager")
    if manager_response.status_code == 201:
        manager_token = login_user("manager_test_user_tasks", "managerpass123")
        if manager_token:
            manager_tasks_response = get_user_tasks(manager_token)
            # Manager should get empty list (no tasks assigned to them)
            success = manager_tasks_response.status_code == 200 and len(manager_tasks_response.json()) == 0
            results["manager_access"] = success
            print_test_result("Manager Access", success, f"Status: {manager_tasks_response.status_code}, Tasks: {len(manager_tasks_response.json())}")
        else:
            results["manager_access"] = False
            print_test_result("Manager Access", False, "Failed to login manager")
    else:
        results["manager_access"] = False
        print_test_result("Manager Access", False, f"Failed to register manager: {manager_response.status_code}")
    
    # Test 3: Register and login as regular user
    print("3. Testing Regular User Access to User Tasks Endpoint")
    user_response = register_user("user_test_user_tasks", "userpass123", "user@test.com", "user")
    if user_response.status_code == 201:
        user_token = login_user("user_test_user_tasks", "userpass123")
        if user_token:
            user_tasks_response = get_user_tasks(user_token)
            # User should get empty list initially (no tasks assigned yet)
            success = user_tasks_response.status_code == 200 and len(user_tasks_response.json()) == 0
            results["user_access"] = success
            print_test_result("User Access", success, f"Status: {user_tasks_response.status_code}, Tasks: {len(user_tasks_response.json())}")
        else:
            results["user_access"] = False
            print_test_result("User Access", False, "Failed to login user")
    else:
        results["user_access"] = False
        print_test_result("User Access", False, f"Failed to register user: {user_response.status_code}")
    
    # Test 4: Create tasks and assign to user, then test endpoint
    print("4. Testing User Tasks Endpoint with Assigned Tasks")
    if user_token:
        # Create a project using admin token
        if admin_token:
            project = create_project(admin_token, "Test Project for User Tasks", "Test project", "2024-01-01", "2024-12-31")
            if project:
                # Create milestone
                milestone = create_milestone(admin_token, "Test Milestone", "Test milestone", "2024-06-30", project['id'])
                if milestone:
                    # Get user ID from user detail
                    user_detail_response = requests.get(f"{BASE_URL}/me/", headers={"Authorization": f"Bearer {user_token}"})
                    if user_detail_response.status_code == 200:
                        user_id = user_detail_response.json()['id']
                        
                        # Create task assigned to user
                        task1 = create_task(admin_token, "Task 1 for User", "First task", milestone['id'], user_id)
                        task2 = create_task(admin_token, "Task 2 for User", "Second task", milestone['id'], user_id)
                        
                        if task1 and task2:
                            # Test user tasks endpoint again
                            user_tasks_response = get_user_tasks(user_token)
                            tasks = user_tasks_response.json()
                            
                            success = (user_tasks_response.status_code == 200 and 
                                     len(tasks) == 2 and
                                     all(task['assignee'] == user_id for task in tasks))
                            
                            results["user_with_tasks"] = success
                            print_test_result("User with Assigned Tasks", success, 
                                            f"Status: {user_tasks_response.status_code}, Tasks: {len(tasks)}")
                            
                            # Verify task details
                            if success:
                                task_titles = [task['title'] for task in tasks]
                                print(f"  Task titles: {task_titles}")
                        else:
                            results["user_with_tasks"] = False
                            print_test_result("User with Assigned Tasks", False, "Failed to create tasks")
                    else:
                        results["user_with_tasks"] = False
                        print_test_result("User with Assigned Tasks", False, "Failed to get user details")
                else:
                    results["user_with_tasks"] = False
                    print_test_result("User with Assigned Tasks", False, "Failed to create milestone")
            else:
                results["user_with_tasks"] = False
                print_test_result("User with Assigned Tasks", False, "Failed to create project")
        else:
            results["user_with_tasks"] = False
            print_test_result("User with Assigned Tasks", False, "No admin token available")
    else:
        results["user_with_tasks"] = False
        print_test_result("User with Assigned Tasks", False, "No user token available")
    
    # Test 5: Test unauthorized access
    print("5. Testing Unauthorized Access")
    unauthorized_response = requests.get(f"{BASE_URL}/user/tasks/")
    success = unauthorized_response.status_code == 401
    results["unauthorized_access"] = success
    print_test_result("Unauthorized Access", success, f"Status: {unauthorized_response.status_code}")
    
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
        success = test_user_tasks_endpoint()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        sys.exit(1) 