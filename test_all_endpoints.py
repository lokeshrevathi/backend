#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all endpoints in the Project Management Dashboard API
"""

import requests
import json
import time
from datetime import datetime, timedelta

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

def test_health_check():
    """Test health check endpoint"""
    print("\n🔍 Testing Health Check")
    response = requests.get(f"{BASE_URL}/health/")
    print_response(response, "Health Check")
    return response.status_code == 200

def test_user_registration():
    """Test user registration"""
    print("\n👤 Testing User Registration")
    timestamp = int(time.time())
    user_data = {
        "username": f"testuser{timestamp}",
        "email": f"test{timestamp}@example.com",
        "password": "testpass123",
        "password2": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    response = requests.post(f"{API_BASE}/register/", json=user_data)
    print_response(response, "User Registration")
    return response.status_code == 201, user_data["username"], "testpass123"

def test_user_login(username, password):
    """Test user login"""
    print("\n🔐 Testing User Login")
    login_data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{API_BASE}/login/", json=login_data)
    print_response(response, "User Login")
    if response.status_code == 200:
        return response.json().get("access")
    return None

def test_user_details(token):
    """Test user details endpoint"""
    print("\n👤 Testing User Details")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/me/", headers=headers)
    print_response(response, "User Details")
    return response.status_code == 200

def test_token_refresh(token):
    """Test token refresh"""
    print("\n🔄 Testing Token Refresh")
    # First get refresh token by logging in again
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    login_response = requests.post(f"{API_BASE}/login/", json=login_data)
    if login_response.status_code == 200:
        refresh_token = login_response.json().get("refresh")
        refresh_data = {"refresh": refresh_token}
        response = requests.post(f"{API_BASE}/token/refresh/", json=refresh_data)
        print_response(response, "Token Refresh")
        return response.status_code == 200
    return False

def test_project_creation(token):
    """Test project creation"""
    print("\n📁 Testing Project Creation")
    headers = {"Authorization": f"Bearer {token}"}
    project_data = {
        "name": "API Test Project",
        "description": "Project created for API testing",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    response = requests.post(f"{API_BASE}/projects/", json=project_data, headers=headers)
    print_response(response, "Project Creation")
    if response.status_code == 201:
        return response.json().get("id")
    return None

def test_project_listing(token):
    """Test project listing"""
    print("\n📋 Testing Project Listing")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/projects/", headers=headers)
    print_response(response, "Project Listing")
    return response.status_code == 200

def test_project_details(token, project_id):
    """Test project details"""
    print("\n📄 Testing Project Details")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/projects/{project_id}/", headers=headers)
    print_response(response, "Project Details")
    return response.status_code == 200

def test_project_update(token, project_id):
    """Test project update"""
    print("\n✏️ Testing Project Update")
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "name": "Updated API Test Project",
        "description": "Updated project description"
    }
    response = requests.put(f"{API_BASE}/projects/{project_id}/", json=update_data, headers=headers)
    print_response(response, "Project Update")
    return response.status_code == 200

def test_milestone_creation(token, project_id):
    """Test milestone creation"""
    print("\n🎯 Testing Milestone Creation")
    headers = {"Authorization": f"Bearer {token}"}
    milestone_data = {
        "title": "Test Milestone",
        "due_date": "2024-06-30",
        "project": project_id
    }
    response = requests.post(f"{API_BASE}/milestones/", json=milestone_data, headers=headers)
    print_response(response, "Milestone Creation")
    if response.status_code == 201:
        return response.json().get("id")
    return None

def test_milestone_listing(token):
    """Test milestone listing"""
    print("\n📋 Testing Milestone Listing")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/milestones/", headers=headers)
    print_response(response, "Milestone Listing")
    return response.status_code == 200

def test_milestone_details(token, milestone_id):
    """Test milestone details"""
    print("\n📄 Testing Milestone Details")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/milestones/{milestone_id}/", headers=headers)
    print_response(response, "Milestone Details")
    return response.status_code == 200

def test_task_creation(token, milestone_id, user_id):
    """Test task creation"""
    print("\n✅ Testing Task Creation")
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {
        "title": "Test Task",
        "description": "Task created for API testing",
        "milestone": milestone_id,
        "assignee": user_id,
        "priority": "high",
        "status": "todo"
    }
    response = requests.post(f"{API_BASE}/tasks/", json=task_data, headers=headers)
    print_response(response, "Task Creation")
    if response.status_code == 201:
        return response.json().get("id")
    return None

def test_task_listing(token):
    """Test task listing"""
    print("\n📋 Testing Task Listing")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/tasks/", headers=headers)
    print_response(response, "Task Listing")
    return response.status_code == 200

def test_task_filtering(token):
    """Test task filtering"""
    print("\n🔍 Testing Task Filtering")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/tasks/?status=todo", headers=headers)
    print_response(response, "Task Filtering (status=todo)")
    return response.status_code == 200

def test_task_details(token, task_id):
    """Test task details"""
    print("\n📄 Testing Task Details")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/tasks/{task_id}/", headers=headers)
    print_response(response, "Task Details")
    return response.status_code == 200

def test_task_update(token, task_id):
    """Test task update"""
    print("\n✏️ Testing Task Update")
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "title": "Updated Test Task",
        "status": "in_progress",
        "priority": "medium"
    }
    response = requests.put(f"{API_BASE}/tasks/{task_id}/", json=update_data, headers=headers)
    print_response(response, "Task Update")
    return response.status_code == 200

def test_time_logging(token, task_id):
    """Test time logging"""
    print("\n⏰ Testing Time Logging")
    headers = {"Authorization": f"Bearer {token}"}
    time_data = {"hours": 4.5}
    response = requests.post(f"{API_BASE}/tasks/{task_id}/log_time/", json=time_data, headers=headers)
    print_response(response, "Time Logging")
    return response.status_code == 200

def test_project_progress(token, project_id):
    """Test project progress"""
    print("\n📊 Testing Project Progress")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/projects/{project_id}/progress/", headers=headers)
    print_response(response, "Project Progress")
    return response.status_code == 200

def test_project_hours(token, project_id):
    """Test project total hours"""
    print("\n⏱️ Testing Project Total Hours")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/projects/{project_id}/total_hours/", headers=headers)
    print_response(response, "Project Total Hours")
    return response.status_code == 200

def test_comment_creation(token, task_id, user_id):
    """Test comment creation"""
    print("\n💬 Testing Comment Creation")
    headers = {"Authorization": f"Bearer {token}"}
    comment_data = {
        "content": "Test comment for API testing",
        "task": task_id,
        "user": user_id
    }
    response = requests.post(f"{API_BASE}/comments/", json=comment_data, headers=headers)
    print_response(response, "Comment Creation")
    if response.status_code == 201:
        return response.json().get("id")
    return None

def test_comment_listing(token):
    """Test comment listing"""
    print("\n📋 Testing Comment Listing")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/comments/", headers=headers)
    print_response(response, "Comment Listing")
    return response.status_code == 200

def test_comment_details(token, comment_id):
    """Test comment details"""
    print("\n📄 Testing Comment Details")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/comments/{comment_id}/", headers=headers)
    print_response(response, "Comment Details")
    return response.status_code == 200

def test_attachment_creation(token, task_id):
    """Test attachment creation"""
    print("\n📎 Testing Attachment Creation")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a simple text file for testing
    files = {
        'file': ('test_file.txt', 'This is a test file content', 'text/plain')
    }
    data = {'task': task_id}
    
    response = requests.post(f"{API_BASE}/attachments/", files=files, data=data, headers=headers)
    print_response(response, "Attachment Creation")
    if response.status_code == 201:
        return response.json().get("id")
    return None

def test_attachment_listing(token):
    """Test attachment listing"""
    print("\n📋 Testing Attachment Listing")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/attachments/", headers=headers)
    print_response(response, "Attachment Listing")
    return response.status_code == 200

def test_unauthorized_access():
    """Test unauthorized access"""
    print("\n🚫 Testing Unauthorized Access")
    response = requests.get(f"{API_BASE}/projects/")
    print_response(response, "Unauthorized Access")
    return response.status_code == 401

def test_invalid_endpoint():
    """Test invalid endpoint"""
    print("\n❌ Testing Invalid Endpoint")
    response = requests.get(f"{API_BASE}/invalid/")
    print_response(response, "Invalid Endpoint")
    return response.status_code == 404

def main():
    """Main test function"""
    print("🚀 Starting Comprehensive API Endpoint Tests")
    print(f"Base URL: {BASE_URL}")
    print(f"API Base: {API_BASE}")
    
    results = {}
    
    # Test 1: Health Check
    results["health_check"] = test_health_check()
    
    # Test 2: User Registration
    reg_success, username, password = test_user_registration()
    results["user_registration"] = reg_success
    
    if not reg_success:
        # Use existing user if registration fails
        username, password = "testuser", "testpass123"
    
    # Test 3: User Login
    token = test_user_login(username, password)
    results["user_login"] = token is not None
    
    if token:
        # Test 4: User Details
        results["user_details"] = test_user_details(token)
        
        # Test 5: Token Refresh
        results["token_refresh"] = test_token_refresh(token)
        
        # Test 6: Project Creation
        project_id = test_project_creation(token)
        results["project_creation"] = project_id is not None
        
        if project_id:
            # Test 7: Project Listing
            results["project_listing"] = test_project_listing(token)
            
            # Test 8: Project Details
            results["project_details"] = test_project_details(token, project_id)
            
            # Test 9: Project Update
            results["project_update"] = test_project_update(token, project_id)
            
            # Test 10: Milestone Creation
            milestone_id = test_milestone_creation(token, project_id)
            results["milestone_creation"] = milestone_id is not None
            
            if milestone_id:
                # Test 11: Milestone Listing
                results["milestone_listing"] = test_milestone_listing(token)
                
                # Test 12: Milestone Details
                results["milestone_details"] = test_milestone_details(token, milestone_id)
                
                # Get user ID for task creation
                user_response = requests.get(f"{API_BASE}/me/", headers={"Authorization": f"Bearer {token}"})
                user_id = user_response.json().get("id") if user_response.status_code == 200 else 1
                
                # Test 13: Task Creation
                task_id = test_task_creation(token, milestone_id, user_id)
                results["task_creation"] = task_id is not None
                
                if task_id:
                    # Test 14: Task Listing
                    results["task_listing"] = test_task_listing(token)
                    
                    # Test 15: Task Filtering
                    results["task_filtering"] = test_task_filtering(token)
                    
                    # Test 16: Task Details
                    results["task_details"] = test_task_details(token, task_id)
                    
                    # Test 17: Task Update
                    results["task_update"] = test_task_update(token, task_id)
                    
                    # Test 18: Time Logging
                    results["time_logging"] = test_time_logging(token, task_id)
                    
                    # Test 19: Project Progress
                    results["project_progress"] = test_project_progress(token, project_id)
                    
                    # Test 20: Project Hours
                    results["project_hours"] = test_project_hours(token, project_id)
                    
                    # Test 21: Comment Creation
                    comment_id = test_comment_creation(token, task_id, user_id)
                    results["comment_creation"] = comment_id is not None
                    
                    if comment_id:
                        # Test 22: Comment Listing
                        results["comment_listing"] = test_comment_listing(token)
                        
                        # Test 23: Comment Details
                        results["comment_details"] = test_comment_details(token, comment_id)
                    
                    # Test 24: Attachment Creation
                    attachment_id = test_attachment_creation(token, task_id)
                    results["attachment_creation"] = attachment_id is not None
                    
                    if attachment_id:
                        # Test 25: Attachment Listing
                        results["attachment_listing"] = test_attachment_listing(token)
    
    # Test 26: Unauthorized Access
    results["unauthorized_access"] = test_unauthorized_access()
    
    # Test 27: Invalid Endpoint
    results["invalid_endpoint"] = test_invalid_endpoint()
    
    # Print Summary
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE API TEST RESULTS")
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
    
    if failed_tests == 0:
        print("\n🎉 All API endpoints are working correctly!")
    else:
        print(f"\n⚠️  {failed_tests} endpoint(s) need attention.")
    
    return results

if __name__ == "__main__":
    main() 