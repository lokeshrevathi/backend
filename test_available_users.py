#!/usr/bin/env python3
"""
Test script for Available Users functionality
Tests the constraint that users already assigned to 2 projects should not be fetched
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = f"admin_test_{int(time.time())}"
REGULAR_USER1 = f"user1_test_{int(time.time())}"
REGULAR_USER2 = f"user2_test_{int(time.time())}"
REGULAR_USER3 = f"user3_test_{int(time.time())}"
REGULAR_USER4 = f"user4_test_{int(time.time())}"

def print_result(test_name, success, details=""):
    """Print test result with formatting"""
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")
    print()

def register_admin():
    """Register an admin user"""
    url = f"{BASE_URL}/api/register/"
    data = {
        "username": ADMIN_USERNAME,
        "email": f"{ADMIN_USERNAME}@example.com",
        "password": "securepass123",
        "password2": "securepass123",
        "first_name": "Admin",
        "last_name": "Test",
        "role": "admin"
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 201:
        print_result("Admin Registration", True, f"Admin created: {ADMIN_USERNAME}")
        return True
    else:
        print_result("Admin Registration", False, f"Status: {response.status_code}, Response: {response.text}")
        return False

def login_admin():
    """Login as admin and get token"""
    url = f"{BASE_URL}/api/login/"
    data = {
        "username": ADMIN_USERNAME,
        "password": "securepass123"
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        token = response.json()['access']
        print_result("Admin Login", True, "Token obtained")
        return token
    else:
        print_result("Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
        return None

def create_regular_user(token, username, role="user"):
    """Create a regular user"""
    url = f"{BASE_URL}/api/users/create/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "securepass123",
        "password2": "securepass123",
        "first_name": "User",
        "last_name": "Test",
        "role": role
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        user_data = response.json()
        print_result(f"Create {role} user", True, f"User created: {username} (ID: {user_data['id']})")
        return user_data['id']
    else:
        print_result(f"Create {role} user", False, f"Status: {response.status_code}, Response: {response.text}")
        return None

def create_project(token, name):
    """Create a project"""
    url = f"{BASE_URL}/api/projects/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": name,
        "description": f"Test project: {name}",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        project_data = response.json()
        print_result(f"Create Project", True, f"Project created: {name} (ID: {project_data['id']})")
        return project_data['id']
    else:
        print_result(f"Create Project", False, f"Status: {response.status_code}, Response: {response.text}")
        return None

def add_user_to_project(token, project_id, user_id):
    """Add a user to a project"""
    url = f"{BASE_URL}/api/projects/{project_id}/members/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"user_id": user_id}
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print_result(f"Add User to Project", True, f"User {user_id} added to project {project_id}")
        return True
    else:
        print_result(f"Add User to Project", False, f"Status: {response.status_code}, Response: {response.text}")
        return False

def get_available_users(token, project_id):
    """Get available users for a project"""
    url = f"{BASE_URL}/api/projects/{project_id}/available-users/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        users = response.json()
        print_result(f"Get Available Users for Project {project_id}", True, f"Found {len(users)} available users")
        return users
    else:
        print_result(f"Get Available Users for Project {project_id}", False, f"Status: {response.status_code}, Response: {response.text}")
        return None

def test_available_users_constraint():
    """Test the available users constraint (max 2 projects per user)"""
    print("=" * 60)
    print("TESTING AVAILABLE USERS CONSTRAINT")
    print("=" * 60)
    
    # Step 1: Register and login as admin
    if not register_admin():
        return False
    
    token = login_admin()
    if not token:
        return False
    
    # Step 2: Create regular users
    user1_id = create_regular_user(token, REGULAR_USER1)
    user2_id = create_regular_user(token, REGULAR_USER2)
    user3_id = create_regular_user(token, REGULAR_USER3)
    user4_id = create_regular_user(token, REGULAR_USER4)
    
    if not all([user1_id, user2_id, user3_id, user4_id]):
        return False
    
    # Step 3: Create projects
    project1_id = create_project(token, "Project 1")
    project2_id = create_project(token, "Project 2")
    project3_id = create_project(token, "Project 3")
    
    if not all([project1_id, project2_id, project3_id]):
        return False
    
    print("\n" + "=" * 40)
    print("TESTING SCENARIO")
    print("=" * 40)
    
    # Step 4: Test initial available users (should include our 4 users)
    print(f"\n1. Initial available users for Project {project1_id}:")
    available_users = get_available_users(token, project1_id)
    if available_users is None:
        return False
    
    # Filter to only our test users
    test_user_ids = [user1_id, user2_id, user3_id, user4_id]
    available_test_users = [user for user in available_users if user['id'] in test_user_ids]
    
    print(f"   Available test users: {[user['username'] for user in available_test_users]}")
    
    if len(available_test_users) == 4:
        print_result("Initial Available Users Check", True, "All 4 test users are available")
    else:
        print_result("Initial Available Users Check", False, f"Expected 4 test users, got {len(available_test_users)}")
        return False
    
    # Step 5: Add user1 to project1
    print(f"\n2. Adding User {user1_id} to Project {project1_id}:")
    if not add_user_to_project(token, project1_id, user1_id):
        return False
    
    # Step 6: Check available users for project1 (should exclude user1)
    print(f"\n3. Available users for Project {project1_id} after adding user1:")
    available_users = get_available_users(token, project1_id)
    if available_users is None:
        return False
    
    # Filter to only our test users
    available_test_users = [user for user in available_users if user['id'] in test_user_ids]
    expected_users = [user2_id, user3_id, user4_id]  # user1 should be excluded
    
    print(f"   Available test users: {[user['username'] for user in available_test_users]}")
    
    available_user_ids = [user['id'] for user in available_test_users]
    if set(available_user_ids) == set(expected_users):
        print_result("Available Users After Adding User1", True, "User1 correctly excluded")
    else:
        print_result("Available Users After Adding User1", False, f"Expected: {expected_users}, Got: {available_user_ids}")
        return False
    
    # Step 7: Add user1 to project2 (user1 now has 2 projects)
    print(f"\n4. Adding User {user1_id} to Project {project2_id} (2nd project):")
    if not add_user_to_project(token, project2_id, user1_id):
        return False
    
    # Step 8: Check available users for project3 (should exclude user1 due to 2-project limit)
    print(f"\n5. Available users for Project {project3_id} (user1 should be excluded due to 2-project limit):")
    available_users = get_available_users(token, project3_id)
    if available_users is None:
        return False
    
    # Filter to only our test users
    available_test_users = [user for user in available_users if user['id'] in test_user_ids]
    expected_users = [user2_id, user3_id, user4_id]  # user1 should be excluded due to 2-project limit
    
    print(f"   Available test users: {[user['username'] for user in available_test_users]}")
    
    available_user_ids = [user['id'] for user in available_test_users]
    if set(available_user_ids) == set(expected_users):
        print_result("Available Users - User1 at Max Limit", True, "User1 correctly excluded due to 2-project limit")
    else:
        print_result("Available Users - User1 at Max Limit", False, f"Expected: {expected_users}, Got: {available_user_ids}")
        return False
    
    # Step 9: Add user2 to project1 and project2 (user2 now has 2 projects)
    print(f"\n6. Adding User {user2_id} to Project {project1_id}:")
    if not add_user_to_project(token, project1_id, user2_id):
        return False
    
    print(f"\n7. Adding User {user2_id} to Project {project2_id} (2nd project):")
    if not add_user_to_project(token, project2_id, user2_id):
        return False
    
    # Step 10: Check available users for project3 (should exclude both user1 and user2)
    print(f"\n8. Available users for Project {project3_id} (both user1 and user2 should be excluded):")
    available_users = get_available_users(token, project3_id)
    if available_users is None:
        return False
    
    # Filter to only our test users
    available_test_users = [user for user in available_users if user['id'] in test_user_ids]
    expected_users = [user3_id, user4_id]  # user1 and user2 should be excluded due to 2-project limit
    
    print(f"   Available test users: {[user['username'] for user in available_test_users]}")
    
    available_user_ids = [user['id'] for user in available_test_users]
    if set(available_user_ids) == set(expected_users):
        print_result("Available Users - Multiple Users at Max Limit", True, "User1 and User2 correctly excluded due to 2-project limit")
    else:
        print_result("Available Users - Multiple Users at Max Limit", False, f"Expected: {expected_users}, Got: {available_user_ids}")
        return False
    
    # Step 11: Test that project owner is excluded
    print(f"\n9. Available users for Project {project1_id} (project owner should be excluded):")
    available_users = get_available_users(token, project1_id)
    if available_users is None:
        return False
    
    # Get project owner ID
    project_response = requests.get(f"{BASE_URL}/api/projects/{project1_id}/", headers={"Authorization": f"Bearer {token}"})
    if project_response.status_code == 200:
        project_owner_id = project_response.json()['owner']
        user_ids = [user['id'] for user in available_users]
        if project_owner_id not in user_ids:
            print_result("Project Owner Exclusion", True, "Project owner correctly excluded from available users")
        else:
            print_result("Project Owner Exclusion", False, f"Project owner {project_owner_id} should not be in available users")
            return False
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("=" * 60)
    print("\nSummary:")
    print("- Users with 'user' role are correctly included")
    print("- Users already members of the project are correctly excluded")
    print("- Users at maximum limit (2 projects) are correctly excluded")
    print("- Project owner is correctly excluded")
    print("- The constraint is working as expected!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_available_users_constraint()
        if success:
            print("\n🎉 Available Users functionality is working correctly!")
        else:
            print("\n❌ Available Users functionality has issues!")
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")
        import traceback
        traceback.print_exc() 