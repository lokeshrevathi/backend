#!/usr/bin/env python3
"""
Test script for Project Members List functionality
Tests the constraint that retrieves only members assigned to that specific project
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = f"admin_members_{int(time.time())}"
REGULAR_USER1 = f"user1_members_{int(time.time())}"
REGULAR_USER2 = f"user2_members_{int(time.time())}"
REGULAR_USER3 = f"user3_members_{int(time.time())}"

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
        "last_name": "Members",
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

def get_project_members(token, project_id):
    """Get project members"""
    url = f"{BASE_URL}/api/projects/{project_id}/members/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        members = response.json()
        print_result(f"Get Project Members for Project {project_id}", True, f"Found {len(members)} members")
        return members
    else:
        print_result(f"Get Project Members for Project {project_id}", False, f"Status: {response.status_code}, Response: {response.text}")
        return None

def test_project_members_list():
    """Test the project members list functionality"""
    print("=" * 60)
    print("TESTING PROJECT MEMBERS LIST FUNCTIONALITY")
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
    
    if not all([user1_id, user2_id, user3_id]):
        return False
    
    # Step 3: Create projects
    project1_id = create_project(token, "Project Alpha")
    project2_id = create_project(token, "Project Beta")
    
    if not all([project1_id, project2_id]):
        return False
    
    print("\n" + "=" * 40)
    print("TESTING SCENARIO")
    print("=" * 40)
    
    # Step 4: Test initial project members (should be empty)
    print(f"\n1. Initial project members for Project {project1_id}:")
    members = get_project_members(token, project1_id)
    if members is None:
        return False
    
    if len(members) == 0:
        print_result("Initial Project Members Check", True, "No members initially (as expected)")
    else:
        print_result("Initial Project Members Check", False, f"Expected 0 members, got {len(members)}")
        return False
    
    # Step 5: Add user1 to project1
    print(f"\n2. Adding User {user1_id} to Project {project1_id}:")
    if not add_user_to_project(token, project1_id, user1_id):
        return False
    
    # Step 6: Check project1 members (should have user1)
    print(f"\n3. Project members for Project {project1_id} after adding user1:")
    members = get_project_members(token, project1_id)
    if members is None:
        return False
    
    member_ids = [member['user']['id'] for member in members]
    if user1_id in member_ids:
        print_result("Project Members After Adding User1", True, f"User1 correctly found in project members: {member_ids}")
    else:
        print_result("Project Members After Adding User1", False, f"Expected user1 ({user1_id}), got: {member_ids}")
        return False
    
    # Step 7: Check project2 members (should still be empty)
    print(f"\n4. Project members for Project {project2_id} (should still be empty):")
    members = get_project_members(token, project2_id)
    if members is None:
        return False
    
    if len(members) == 0:
        print_result("Project2 Members Check", True, "Project2 correctly has no members")
    else:
        print_result("Project2 Members Check", False, f"Expected 0 members, got {len(members)}")
        return False
    
    # Step 8: Add user2 to project1
    print(f"\n5. Adding User {user2_id} to Project {project1_id}:")
    if not add_user_to_project(token, project1_id, user2_id):
        return False
    
    # Step 9: Check project1 members (should have user1 and user2)
    print(f"\n6. Project members for Project {project1_id} after adding user2:")
    members = get_project_members(token, project1_id)
    if members is None:
        return False
    
    member_ids = [member['user']['id'] for member in members]
    expected_ids = [user1_id, user2_id]
    if set(member_ids) == set(expected_ids):
        print_result("Project Members After Adding User2", True, f"Both users correctly found: {member_ids}")
    else:
        print_result("Project Members After Adding User2", False, f"Expected: {expected_ids}, Got: {member_ids}")
        return False
    
    # Step 10: Add user3 to project2
    print(f"\n7. Adding User {user3_id} to Project {project2_id}:")
    if not add_user_to_project(token, project2_id, user3_id):
        return False
    
    # Step 11: Check project2 members (should have user3)
    print(f"\n8. Project members for Project {project2_id} after adding user3:")
    members = get_project_members(token, project2_id)
    if members is None:
        return False
    
    member_ids = [member['user']['id'] for member in members]
    if user3_id in member_ids and len(member_ids) == 1:
        print_result("Project2 Members After Adding User3", True, f"User3 correctly found: {member_ids}")
    else:
        print_result("Project2 Members After Adding User3", False, f"Expected user3 ({user3_id}), got: {member_ids}")
        return False
    
    # Step 12: Verify project1 still has user1 and user2 (isolation test)
    print(f"\n9. Verifying Project {project1_id} still has correct members (isolation test):")
    members = get_project_members(token, project1_id)
    if members is None:
        return False
    
    member_ids = [member['user']['id'] for member in members]
    expected_ids = [user1_id, user2_id]
    if set(member_ids) == set(expected_ids):
        print_result("Project1 Isolation Test", True, f"Project1 correctly isolated: {member_ids}")
    else:
        print_result("Project1 Isolation Test", False, f"Expected: {expected_ids}, Got: {member_ids}")
        return False
    
    # Step 13: Test member details structure
    print(f"\n10. Testing member details structure:")
    members = get_project_members(token, project1_id)
    if members and len(members) > 0:
        member = members[0]
        required_fields = ['id', 'user', 'joined_at']
        user_fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        
        # Check member fields
        member_fields_ok = all(field in member for field in required_fields)
        # Check user fields
        user_fields_ok = all(field in member['user'] for field in user_fields)
        
        if member_fields_ok and user_fields_ok:
            print_result("Member Structure Test", True, "Member structure is correct")
            print(f"   Member fields: {list(member.keys())}")
            print(f"   User fields: {list(member['user'].keys())}")
        else:
            print_result("Member Structure Test", False, f"Missing fields in member structure")
            return False
    else:
        print_result("Member Structure Test", False, "No members to test structure")
        return False
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("=" * 60)
    print("\nSummary:")
    print("- Project members are correctly retrieved for specific projects")
    print("- Members are isolated between different projects")
    print("- Member structure includes all required fields")
    print("- The constraint is working as expected!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_project_members_list()
        if success:
            print("\n🎉 Project Members List functionality is working correctly!")
        else:
            print("\n❌ Project Members List functionality has issues!")
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")
        import traceback
        traceback.print_exc() 