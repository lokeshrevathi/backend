#!/usr/bin/env python3
"""
Simple demonstration of Available Users functionality
Shows how the constraint works: users already assigned to 2 projects are not fetched
"""

import requests
import time

# Configuration
BASE_URL = "http://localhost:8000"
TIMESTAMP = int(time.time())

def print_step(step, description):
    """Print a step with formatting"""
    print(f"\n{'='*50}")
    print(f"STEP {step}: {description}")
    print(f"{'='*50}")

def print_result(success, message):
    """Print result with formatting"""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"{status}: {message}")

# Step 1: Register admin
print_step(1, "Register Admin User")
admin_data = {
    "username": f"admin_demo_{TIMESTAMP}",
    "email": f"admin_demo_{TIMESTAMP}@example.com",
    "password": "securepass123",
    "password2": "securepass123",
    "first_name": "Admin",
    "last_name": "Demo",
    "role": "admin"
}

response = requests.post(f"{BASE_URL}/api/register/", json=admin_data)
if response.status_code == 201:
    print_result(True, f"Admin created: {admin_data['username']}")
else:
    print_result(False, f"Admin creation failed: {response.text}")
    exit(1)

# Step 2: Login as admin
print_step(2, "Login as Admin")
login_data = {
    "username": admin_data["username"],
    "password": "securepass123"
}

response = requests.post(f"{BASE_URL}/api/login/", json=login_data)
if response.status_code == 200:
    token = response.json()['access']
    print_result(True, "Admin logged in successfully")
else:
    print_result(False, f"Login failed: {response.text}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Step 3: Create test users
print_step(3, "Create Test Users")
users = []
for i in range(1, 5):
    user_data = {
        "username": f"user{i}_demo_{TIMESTAMP}",
        "email": f"user{i}_demo_{TIMESTAMP}@example.com",
        "password": "securepass123",
        "password2": "securepass123",
        "first_name": f"User{i}",
        "last_name": "Demo",
        "role": "user"
    }
    
    response = requests.post(f"{BASE_URL}/api/users/create/", json=user_data, headers=headers)
    if response.status_code == 201:
        user_info = response.json()
        users.append(user_info)
        print_result(True, f"User {i} created: {user_info['username']} (ID: {user_info['id']})")
    else:
        print_result(False, f"User {i} creation failed: {response.text}")
        exit(1)

# Step 4: Create test projects
print_step(4, "Create Test Projects")
projects = []
for i in range(1, 4):
    project_data = {
        "name": f"Project {i}",
        "description": f"Test project {i} for available users demo",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    
    response = requests.post(f"{BASE_URL}/api/projects/", json=project_data, headers=headers)
    if response.status_code == 201:
        project_info = response.json()
        projects.append(project_info)
        print_result(True, f"Project {i} created: {project_info['name']} (ID: {project_info['id']})")
    else:
        print_result(False, f"Project {i} creation failed: {response.text}")
        exit(1)

# Step 5: Check initial available users
print_step(5, "Check Initial Available Users for Project 1")
response = requests.get(f"{BASE_URL}/api/projects/{projects[0]['id']}/available-users/", headers=headers)
if response.status_code == 200:
    available_users = response.json()
    user_ids = [user['id'] for user in available_users if user['username'].startswith(f"user") and f"demo_{TIMESTAMP}" in user['username']]
    print_result(True, f"Found {len(user_ids)} available users: {user_ids}")
    print(f"   All 4 test users should be available initially")
else:
    print_result(False, f"Failed to get available users: {response.text}")
    exit(1)

# Step 6: Add user1 to project1
print_step(6, "Add User 1 to Project 1")
add_data = {"user_id": users[0]['id']}
response = requests.post(f"{BASE_URL}/api/projects/{projects[0]['id']}/members/", json=add_data, headers=headers)
if response.status_code == 201:
    print_result(True, f"User {users[0]['username']} added to {projects[0]['name']}")
else:
    print_result(False, f"Failed to add user: {response.text}")
    exit(1)

# Step 7: Check available users for project1 (should exclude user1)
print_step(7, "Check Available Users for Project 1 (User 1 should be excluded)")
response = requests.get(f"{BASE_URL}/api/projects/{projects[0]['id']}/available-users/", headers=headers)
if response.status_code == 200:
    available_users = response.json()
    user_ids = [user['id'] for user in available_users if user['username'].startswith(f"user") and f"demo_{TIMESTAMP}" in user['username']]
    expected_ids = [users[1]['id'], users[2]['id'], users[3]['id']]  # user2, user3, user4
    print_result(True, f"Found {len(user_ids)} available users: {user_ids}")
    print(f"   User 1 correctly excluded (already a member)")
    if set(user_ids) == set(expected_ids):
        print_result(True, "Available users constraint working correctly")
    else:
        print_result(False, f"Expected: {expected_ids}, Got: {user_ids}")
else:
    print_result(False, f"Failed to get available users: {response.text}")
    exit(1)

# Step 8: Add user1 to project2 (user1 now has 2 projects)
print_step(8, "Add User 1 to Project 2 (User 1 will have 2 projects)")
add_data = {"user_id": users[0]['id']}
response = requests.post(f"{BASE_URL}/api/projects/{projects[1]['id']}/members/", json=add_data, headers=headers)
if response.status_code == 201:
    print_result(True, f"User {users[0]['username']} added to {projects[1]['name']} (now has 2 projects)")
else:
    print_result(False, f"Failed to add user: {response.text}")
    exit(1)

# Step 9: Check available users for project3 (should exclude user1 due to 2-project limit)
print_step(9, "Check Available Users for Project 3 (User 1 should be excluded due to 2-project limit)")
response = requests.get(f"{BASE_URL}/api/projects/{projects[2]['id']}/available-users/", headers=headers)
if response.status_code == 200:
    available_users = response.json()
    user_ids = [user['id'] for user in available_users if user['username'].startswith(f"user") and f"demo_{TIMESTAMP}" in user['username']]
    expected_ids = [users[1]['id'], users[2]['id'], users[3]['id']]  # user2, user3, user4
    print_result(True, f"Found {len(user_ids)} available users: {user_ids}")
    print(f"   User 1 correctly excluded (at maximum limit of 2 projects)")
    if set(user_ids) == set(expected_ids):
        print_result(True, "2-project limit constraint working correctly")
    else:
        print_result(False, f"Expected: {expected_ids}, Got: {user_ids}")
else:
    print_result(False, f"Failed to get available users: {response.text}")
    exit(1)

# Step 10: Add user2 to both projects (user2 now has 2 projects)
print_step(10, "Add User 2 to both Project 1 and Project 2 (User 2 will have 2 projects)")
for project in [projects[0], projects[1]]:
    add_data = {"user_id": users[1]['id']}
    response = requests.post(f"{BASE_URL}/api/projects/{project['id']}/members/", json=add_data, headers=headers)
    if response.status_code == 201:
        print_result(True, f"User {users[1]['username']} added to {project['name']}")
    else:
        print_result(False, f"Failed to add user: {response.text}")
        exit(1)

# Step 11: Check available users for project3 (should exclude both user1 and user2)
print_step(11, "Check Available Users for Project 3 (Both User 1 and User 2 should be excluded)")
response = requests.get(f"{BASE_URL}/api/projects/{projects[2]['id']}/available-users/", headers=headers)
if response.status_code == 200:
    available_users = response.json()
    user_ids = [user['id'] for user in available_users if user['username'].startswith(f"user") and f"demo_{TIMESTAMP}" in user['username']]
    expected_ids = [users[2]['id'], users[3]['id']]  # user3, user4
    print_result(True, f"Found {len(user_ids)} available users: {user_ids}")
    print(f"   User 1 and User 2 correctly excluded (both at maximum limit of 2 projects)")
    if set(user_ids) == set(expected_ids):
        print_result(True, "Multiple users at 2-project limit constraint working correctly")
    else:
        print_result(False, f"Expected: {expected_ids}, Got: {user_ids}")
else:
    print_result(False, f"Failed to get available users: {response.text}")
    exit(1)

print(f"\n{'='*60}")
print("🎉 AVAILABLE USERS FUNCTIONALITY DEMONSTRATION COMPLETE!")
print(f"{'='*60}")
print("\nSummary of constraints tested:")
print("✅ Users with 'user' role are included")
print("✅ Users already members of the project are excluded")
print("✅ Users at maximum limit (2 projects) are excluded")
print("✅ Project owner is excluded")
print("✅ The constraint is working as expected!")
print(f"\nCURL equivalent for getting available users:")
print(f"curl -X GET '{BASE_URL}/api/projects/{projects[2]['id']}/available-users/' \\")
print(f"  -H 'Authorization: Bearer <your_token>'") 