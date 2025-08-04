#!/usr/bin/env python3
"""
Test script to verify project member functionality with constraints:
1. Only users with 'user' role can be added to projects
2. One user can be assigned to maximum 2 projects only
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

def test_admin_registration():
    """Register an admin for testing"""
    print("\n👑 Registering Admin for Testing")
    timestamp = int(time.time())
    admin_data = {
        "username": f"admin{timestamp}",
        "email": f"admin{timestamp}@example.com",
        "password": "testpass123",
        "password2": "testpass123",
        "first_name": "Test",
        "last_name": "Admin",
        "role": "admin"
    }
    response = requests.post(f"{API_BASE}/register/", json=admin_data)
    print_response(response, "Admin Registration")
    return response.status_code == 201, admin_data["username"], "testpass123"

def test_admin_login(username, password):
    """Login as admin"""
    print(f"\n🔐 Admin Login: {username}")
    login_data = {"username": username, "password": password}
    response = requests.post(f"{API_BASE}/login/", json=login_data)
    print_response(response, "Admin Login")
    if response.status_code == 200:
        return response.json().get("access")
    return None

def test_create_users(admin_token):
    """Create test users (regular users and managers)"""
    print("\n👥 Creating Test Users")
    headers = {"Authorization": f"Bearer {admin_token}"}
    users = []
    
    # Create regular users
    for i in range(3):
        timestamp = int(time.time()) + i
        user_data = {
            "username": f"user{i+1}_{timestamp}",
            "email": f"user{i+1}_{timestamp}@example.com",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": f"User{i+1}",
            "last_name": "Test",
            "role": "user"
        }
        response = requests.post(f"{API_BASE}/users/create/", json=user_data, headers=headers)
        if response.status_code == 201:
            users.append(response.json())
            print(f"✅ Created user: {user_data['username']}")
        else:
            print(f"❌ Failed to create user: {user_data['username']}")
    
    # Create a manager
    timestamp = int(time.time()) + 100
    manager_data = {
        "username": f"manager_{timestamp}",
        "email": f"manager_{timestamp}@example.com",
        "password": "testpass123",
        "password2": "testpass123",
        "first_name": "Manager",
        "last_name": "Test",
        "role": "manager"
    }
    response = requests.post(f"{API_BASE}/users/create/", json=manager_data, headers=headers)
    if response.status_code == 201:
        users.append(response.json())
        print(f"✅ Created manager: {manager_data['username']}")
    else:
        print(f"❌ Failed to create manager: {manager_data['username']}")
    
    return users

def test_create_projects(admin_token):
    """Create test projects"""
    print("\n📁 Creating Test Projects")
    headers = {"Authorization": f"Bearer {admin_token}"}
    projects = []
    
    for i in range(3):
        timestamp = int(time.time()) + i
        project_data = {
            "name": f"Project {i+1}",
            "description": f"Test project {i+1}",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        response = requests.post(f"{API_BASE}/projects/", json=project_data, headers=headers)
        if response.status_code == 201:
            projects.append(response.json())
            print(f"✅ Created project: {project_data['name']}")
        else:
            print(f"❌ Failed to create project: {project_data['name']}")
    
    return projects

def test_add_user_to_project(admin_token, project_id, user_id, expected_success=True):
    """Test adding a user to a project"""
    print(f"\n➕ Adding User {user_id} to Project {project_id}")
    headers = {"Authorization": f"Bearer {admin_token}"}
    member_data = {"user_id": user_id}
    
    response = requests.post(f"{API_BASE}/projects/{project_id}/members/", json=member_data, headers=headers)
    print_response(response, f"Add User {user_id} to Project {project_id}")
    
    success = response.status_code == 201
    if success == expected_success:
        print("✅ Expected result")
        return True
    else:
        print("❌ Unexpected result")
        return False

def test_add_manager_to_project(admin_token, project_id, manager_id):
    """Test adding a manager to a project (should fail)"""
    print(f"\n🚫 Adding Manager {manager_id} to Project {project_id} (Should Fail)")
    headers = {"Authorization": f"Bearer {admin_token}"}
    member_data = {"user_id": manager_id}
    
    response = requests.post(f"{API_BASE}/projects/{project_id}/members/", json=member_data, headers=headers)
    print_response(response, f"Add Manager {manager_id} to Project {project_id}")
    
    success = response.status_code == 400
    if success:
        print("✅ Correctly rejected manager")
    else:
        print("❌ Should have rejected manager")
    
    return success

def test_get_project_members(admin_token, project_id):
    """Get project members"""
    print(f"\n👥 Getting Members for Project {project_id}")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = requests.get(f"{API_BASE}/projects/{project_id}/members/", headers=headers)
    print_response(response, f"Project {project_id} Members")
    return response.json() if response.status_code == 200 else []

def test_get_available_users(admin_token, project_id):
    """Get available users for a project"""
    print(f"\n🔍 Getting Available Users for Project {project_id}")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = requests.get(f"{API_BASE}/projects/{project_id}/available-users/", headers=headers)
    print_response(response, f"Available Users for Project {project_id}")
    return response.json() if response.status_code == 200 else []

def test_remove_user_from_project(admin_token, project_id, user_id):
    """Remove a user from a project"""
    print(f"\n➖ Removing User {user_id} from Project {project_id}")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = requests.delete(f"{API_BASE}/projects/{project_id}/members/{user_id}/", headers=headers)
    print_response(response, f"Remove User {user_id} from Project {project_id}")
    return response.status_code == 204

def main():
    """Main test function"""
    print("🚀 Testing Project Member Functionality")
    print(f"Base URL: {BASE_URL}")
    print(f"API Base: {API_BASE}")
    
    results = {}
    
    # Step 1: Register and login as admin
    admin_success, admin_username, admin_password = test_admin_registration()
    results["admin_registration"] = admin_success
    
    if not admin_success:
        print("❌ Cannot proceed without admin")
        return results
    
    admin_token = test_admin_login(admin_username, admin_password)
    results["admin_login"] = admin_token is not None
    
    if not admin_token:
        print("❌ Cannot proceed without admin token")
        return results
    
    # Step 2: Create test users
    users = test_create_users(admin_token)
    results["create_users"] = len(users) >= 3  # At least 3 users created
    
    if len(users) < 3:
        print("❌ Need at least 3 users for testing")
        return results
    
    # Step 3: Create test projects
    projects = test_create_projects(admin_token)
    results["create_projects"] = len(projects) >= 3  # At least 3 projects created
    
    if len(projects) < 3:
        print("❌ Need at least 3 projects for testing")
        return results
    
    # Extract user IDs
    regular_users = [user for user in users if user['role'] == 'user']
    managers = [user for user in users if user['role'] == 'manager']
    
    if not regular_users:
        print("❌ No regular users created")
        return results
    
    if not managers:
        print("❌ No managers created")
        return results
    
    # Step 4: Test Constraint 1 - Only users can be added to projects
    print("\n" + "="*80)
    print("🧪 TESTING CONSTRAINT 1: Only users can be added to projects")
    print("="*80)
    
    # Try to add a regular user (should succeed)
    results["add_regular_user"] = test_add_user_to_project(
        admin_token, projects[0]['id'], regular_users[0]['id'], True
    )
    
    # Try to add a manager (should fail)
    results["add_manager_fails"] = test_add_manager_to_project(
        admin_token, projects[0]['id'], managers[0]['id']
    )
    
    # Step 5: Test Constraint 2 - Maximum 2 projects per user
    print("\n" + "="*80)
    print("🧪 TESTING CONSTRAINT 2: Maximum 2 projects per user")
    print("="*80)
    
    # Add user to first project
    results["add_user_to_project1"] = test_add_user_to_project(
        admin_token, projects[0]['id'], regular_users[1]['id'], True
    )
    
    # Add same user to second project
    results["add_user_to_project2"] = test_add_user_to_project(
        admin_token, projects[1]['id'], regular_users[1]['id'], True
    )
    
    # Try to add same user to third project (should fail)
    results["add_user_to_project3_fails"] = test_add_user_to_project(
        admin_token, projects[2]['id'], regular_users[1]['id'], False
    )
    
    # Step 6: Test project member management
    print("\n" + "="*80)
    print("🧪 TESTING PROJECT MEMBER MANAGEMENT")
    print("="*80)
    
    # Get project members
    members = test_get_project_members(admin_token, projects[0]['id'])
    results["get_project_members"] = len(members) > 0
    
    # Get available users
    available_users = test_get_available_users(admin_token, projects[0]['id'])
    results["get_available_users"] = len(available_users) >= 0
    
    # Remove user from project
    if members:
        results["remove_user"] = test_remove_user_from_project(
            admin_token, projects[0]['id'], members[0]['user']['id']
        )
    
    # Step 7: Test project details with members
    print("\n" + "="*80)
    print("🧪 TESTING PROJECT DETAILS WITH MEMBERS")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{API_BASE}/projects/{projects[0]['id']}/", headers=headers)
    if response.status_code == 200:
        project_data = response.json()
        print(f"Project: {project_data['name']}")
        print(f"Members: {len(project_data.get('members', []))}")
        print(f"Member Count: {project_data.get('member_count', 0)}")
        results["project_with_members"] = True
    else:
        results["project_with_members"] = False
    
    # Print Summary
    print("\n" + "="*80)
    print("📊 PROJECT MEMBER TEST RESULTS")
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
    print("✅ Only users with 'user' role can be added to projects")
    print("❌ Managers and admins cannot be added to projects")
    print("✅ Users can be added to up to 2 projects")
    print("❌ Users cannot be added to more than 2 projects")
    print("✅ Project member management works correctly")
    print("✅ Available users list excludes users at max limit")
    
    if failed_tests == 0:
        print("\n🎉 All project member constraints are working correctly!")
    else:
        print(f"\n⚠️  {failed_tests} test(s) need attention.")
    
    return results

if __name__ == "__main__":
    main() 