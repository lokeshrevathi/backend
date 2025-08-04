# Project Management Dashboard API Documentation

## Overview
This API provides comprehensive endpoints for managing projects, milestones, tasks, comments, and attachments with role-based access control (RBAC). The system supports three user roles: `admin`, `manager`, and `user`, each with specific permissions and access levels.

## Table of Contents
1. [Authentication](#authentication)
2. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
3. [Base URL](#base-url)
4. [Response Format](#response-format)
5. [Error Handling](#error-handling)
6. [API Endpoints](#api-endpoints)
7. [Examples](#examples)
8. [Design Justifications](#design-justifications)

## Authentication
All endpoints (except registration, login, token refresh, and health check) require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Role-Based Access Control (RBAC)

### User Roles
- **Admin**: Can create users & managers, access all data, manage project members
- **Manager**: Can create projects/milestones, assign users, assign tasks, manage project members
- **User**: Can access only their assigned tasks and owned/member projects

### Permission Matrix
| Action | Admin | Manager | User |
|--------|-------|---------|------|
| Create Users/Managers | ✅ | ❌ | ❌ |
| Create Projects | ✅ | ✅ | ✅ |
| Create Milestones | ✅ | ✅ | ✅ |
| Create Tasks | ✅ | ✅ | ✅ |
| Assign Users to Tasks | ✅ | ✅ | ❌ |
| Assign Tasks | ✅ | ✅ | ❌ |
| Manage Project Members | ✅ | ✅ | ❌ |
| Access All Projects | ✅ | ✅ | ❌ |
| Access All Tasks | ✅ | ✅ | ❌ |
| Access Own/Member Projects | ✅ | ✅ | ✅ |
| Access Assigned Tasks | ✅ | ✅ | ✅ |
| Create Comments | ✅ | ✅ | ✅ |
| Upload Attachments | ✅ | ✅ | ✅ |
| Log Time | ✅ | ✅ | ✅ |

## Base URL
```
http://localhost:8000
```

## Response Format
All API responses are in JSON format with the following structure:
- **Success**: HTTP status codes 200, 201, 204
- **Error**: HTTP status codes 400, 401, 403, 404, 500

## Error Handling
The API returns consistent error responses:
```json
{
  "detail": "Error message",
  "code": "error_code"
}
```

## API Endpoints

### 1. System Health

#### Health Check
**GET** `/health/`
- **Description**: Check if the API is running
- **Authentication**: Not required
- **Response**: `{"status": "healthy"}`

**Example**:
```bash
curl -X GET http://localhost:8000/health/
```

### 2. Authentication & User Management

#### User Registration
**POST** `/api/register/`
- **Description**: Register a new admin (public registration for admin role only)
- **Authentication**: Not required
- **Required Fields**:
  - `username` (string)
  - `email` (string)
  - `password` (string)
  - `password2` (string)
  - `first_name` (string)
  - `last_name` (string)
  - `role` (string, must be 'admin' for public registration)
- **Response Fields**: `username`, `email`, `first_name`, `last_name`, `role`
- **Note**: 
  - Public registration only allows 'admin' role
  - 'User' and 'Manager' roles can only be created by authenticated admins via `/api/users/create/`

**Example**:
```bash
# Register an admin (public registration)
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_user",
    "email": "admin@example.com",
    "password": "securepass123",
    "password2": "securepass123",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin"
  }'
```

#### User Creation (Admin Only)
**POST** `/api/users/create/`
- **Description**: Create a new user with specific role (Admin only - for creating users and managers)
- **Authentication**: Required (Admin)
- **Required Fields**:
  - `username` (string)
  - `email` (string)
  - `password` (string)
  - `password2` (string)
  - `first_name` (string)
  - `last_name` (string)
  - `role` (string: admin, manager, or user)
- **Response Fields**: `id`, `username`, `email`, `first_name`, `last_name`, `role`
- **Note**: This endpoint is specifically for admins to create users and managers

**Example**:
```bash
# Create a regular user (admin only)
curl -X POST http://localhost:8000/api/users/create/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "regular_user",
    "email": "user@example.com",
    "password": "securepass123",
    "password2": "securepass123",
    "first_name": "Regular",
    "last_name": "User",
    "role": "user"
  }'

# Create a manager (admin only)
curl -X POST http://localhost:8000/api/users/create/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "manager_jane",
    "email": "jane@example.com",
    "password": "securepass123",
    "password2": "securepass123",
    "first_name": "Jane",
    "last_name": "Manager",
    "role": "manager"
  }'
```

#### User Login
**POST** `/api/login/`
- **Description**: Login and get JWT tokens
- **Authentication**: Not required
- **Required Fields**:
  - `username` (string)
  - `password` (string)
- **Response Fields**: `access`, `refresh`

**Example**:
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepass123"
  }'
```

#### Token Refresh
**POST** `/api/token/refresh/`
- **Description**: Refresh JWT access token
- **Authentication**: Not required
- **Required Fields**:
  - `refresh` (string)
- **Response Fields**: `access`

**Example**:
```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "your_refresh_token_here"
  }'
```

#### User Details
**GET** `/api/me/`
- **Description**: Get current user details
- **Authentication**: Required
- **Response Fields**: `id`, `username`, `email`, `first_name`, `last_name`, `role`

**Example**:
```bash
curl -X GET http://localhost:8000/api/me/ \
  -H "Authorization: Bearer <your_token>"
```

### 3. Project Management

#### List/Create Projects
**GET/POST** `/api/projects/`
- **Description**: List projects (filtered by role) or create new project
- **Authentication**: Required
- **Required Fields** (for POST):
  - `name` (string)
  - `description` (string)
  - `start_date` (date: YYYY-MM-DD)
  - `end_date` (date: YYYY-MM-DD)
- **Response Fields**: `id`, `owner`, `name`, `description`, `start_date`, `end_date`, `members`, `member_count`
- **Permissions**: 
  - GET: All authenticated users (filtered by role)
  - POST: All authenticated users
- **Note**: Users see projects they own or are members of, admins/managers see all projects

**Example**:
```bash
# Create Project
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Website Redesign",
    "description": "Redesign company website with modern UI/UX",
    "start_date": "2024-01-01",
    "end_date": "2024-06-30"
  }'

# List Projects
curl -X GET http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer <token>"
```

#### Project Details
**GET/PUT/DELETE** `/api/projects/{id}/`
- **Description**: Get, update, or delete a project
- **Authentication**: Required
- **Permissions**: Project owner, manager, or admin
- **Response Fields**: `id`, `owner`, `name`, `description`, `start_date`, `end_date`, `members`, `member_count`
- **Note**: Update operations allow partial updates (fields are optional)

**Example**:
```bash
# Get Project
curl -X GET http://localhost:8000/api/projects/1/ \
  -H "Authorization: Bearer <token>"

# Update Project
curl -X PUT http://localhost:8000/api/projects/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Website Redesign",
    "description": "Updated project description"
  }'

# Delete Project
curl -X DELETE http://localhost:8000/api/projects/1/ \
  -H "Authorization: Bearer <token>"
```

#### Project Member Management

##### List Project Members
**GET** `/api/projects/{project_id}/members/`
- **Description**: Get all members assigned to a specific project
- **Authentication**: Required (Admin/Manager)
- **Response Fields**: `id`, `user`, `project`, `joined_at`
- **Constraint**: Retrieves only the members assigned to that specific project
- **Note**: Returns project members (excluding project owner)

**Example**:
```bash
curl -X GET http://localhost:8000/api/projects/1/members/ \
  -H "Authorization: Bearer <token>"
```

**Response Example**:
```json
[
  {
    "id": 1,
    "user": {
      "id": 2,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "user"
    },
    "project": 1,
    "joined_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "user": {
      "id": 3,
      "username": "jane_smith",
      "email": "jane@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "role": "user"
    },
    "project": 1,
    "joined_at": "2024-01-16T14:20:00Z"
  }
]
```

##### Add User to Project
**POST** `/api/projects/{project_id}/members/`
- **Description**: Add a user as a member to a project
- **Authentication**: Required (Admin/Manager)
- **Required Fields**:
  - `user_id` (integer: user ID)
- **Constraints**:
  - Only users with 'user' role can be added
  - Maximum 2 projects per user
  - User cannot be project owner
  - User cannot already be a member
- **Response Fields**: `id`, `user`, `project`, `joined_at`

**Example**:
```bash
curl -X POST http://localhost:8000/api/projects/1/members/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2
  }'
```

##### Remove User from Project
**DELETE** `/api/projects/{project_id}/members/{user_id}/`
- **Description**: Remove a user from a project
- **Authentication**: Required (Admin/Manager)
- **Response**: 204 No Content

**Example**:
```bash
curl -X DELETE http://localhost:8000/api/projects/1/members/2/ \
  -H "Authorization: Bearer <token>"
```

##### Get Available Users for Project
**GET** `/api/projects/{project_id}/available-users/`
- **Description**: Get list of users who can be added to the project
- **Authentication**: Required (Admin/Manager)
- **Response Fields**: `id`, `username`, `email`, `first_name`, `last_name`, `role`
- **Constraints**: 
  - Only users with 'user' role are included
  - Users already members of the project are excluded
  - Users at maximum limit (2 projects) are excluded
  - Project owner is excluded
- **Note**: This endpoint implements the constraint that users already assigned to 2 projects are not fetched

**Example**:
```bash
curl -X GET http://localhost:8000/api/projects/1/available-users/ \
  -H "Authorization: Bearer <token>"
```

**Response Example**:
```json
[
  {
    "id": 2,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user"
  },
  {
    "id": 3,
    "username": "jane_smith",
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "role": "user"
  }
]
```

#### Project Progress
**GET** `/api/projects/{id}/progress/`
- **Description**: Get project completion percentage
- **Authentication**: Required
- **Permissions**: Project owner, manager, or admin
- **Response Fields**: `project_id`, `progress_percent`

**Example**:
```bash
curl -X GET http://localhost:8000/api/projects/1/progress/ \
  -H "Authorization: Bearer <token>"
```

#### Project Total Hours
**GET** `/api/projects/{id}/total_hours/`
- **Description**: Get total hours logged for project
- **Authentication**: Required
- **Permissions**: Project owner, manager, or admin
- **Response Fields**: `project_id`, `total_hours`

**Example**:
```bash
curl -X GET http://localhost:8000/api/projects/1/total_hours/ \
  -H "Authorization: Bearer <token>"
```

### 4. Milestone Management

#### List/Create Milestones
**GET/POST** `/api/milestones/`
- **Description**: List milestones (filtered by role) or create new milestone
- **Authentication**: Required
- **Required Fields** (for POST):
  - `title` (string)
  - `due_date` (date: YYYY-MM-DD)
  - `project` (integer: project ID)
- **Response Fields**: `id`, `title`, `due_date`, `project`
- **Permissions**: 
  - GET: All authenticated users (filtered by role)
  - POST: All authenticated users
- **Note**: Users see milestones of projects they own or are members of, admins/managers see all milestones

**Example**:
```bash
# Create Milestone
curl -X POST http://localhost:8000/api/milestones/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Design Phase Complete",
    "due_date": "2024-03-15",
    "project": 1
  }'

# List Milestones
curl -X GET http://localhost:8000/api/milestones/ \
  -H "Authorization: Bearer <token>"
```

#### Milestone Details
**GET/PUT/DELETE** `/api/milestones/{id}/`
- **Description**: Get, update, or delete a milestone
- **Authentication**: Required
- **Permissions**: Project owner, manager, or admin
- **Note**: Update operations allow partial updates (fields are optional)

**Example**:
```bash
# Get Milestone
curl -X GET http://localhost:8000/api/milestones/1/ \
  -H "Authorization: Bearer <token>"

# Update Milestone
curl -X PUT http://localhost:8000/api/milestones/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Design Phase",
    "due_date": "2024-03-20"
  }'

# Delete Milestone
curl -X DELETE http://localhost:8000/api/milestones/1/ \
  -H "Authorization: Bearer <token>"
```

### 5. Task Management

#### List/Create Tasks
**GET/POST** `/api/tasks/`
- **Description**: List tasks (filtered by role) or create new task
- **Authentication**: Required
- **Required Fields** (for POST):
  - `title` (string)
  - `milestone` (integer: milestone ID)
  - `priority` (string: low, medium, high)
  - `status` (string: todo, in_progress, done)
- **Optional Fields**:
  - `description` (string)
  - `assignee` (integer: user ID)
- **Response Fields**: `id`, `title`, `description`, `status`, `priority`, `assignee`, `milestone`, `logged_hours`
- **Filters**: `status`, `assignee` (query parameters)
- **Permissions**: 
  - GET: All authenticated users (filtered by role)
  - POST: All authenticated users
- **Note**: Users see tasks assigned to them or from projects they own/are members of, admins/managers see all tasks

#### Get User Tasks
**GET** `/api/user/tasks/`
- **Description**: Get tasks assigned to the authenticated user (user role only)
- **Authentication**: Required
- **Permissions**: All authenticated users (but only returns tasks for users with 'user' role)
- **Response Fields**: `id`, `title`, `description`, `status`, `priority`, `assignee`, `milestone`, `logged_hours`
- **Constraints**: 
  - Only returns tasks directly assigned to the requesting user
  - Users with 'admin' or 'manager' role will get empty list (no tasks assigned to them)
  - Designed specifically for users with 'user' role to see their assigned tasks
- **Note**: This endpoint is different from `/api/tasks/` which shows tasks based on project ownership/membership

**Example**:
```bash
# Get User Tasks (for users with 'user' role)
curl -X GET http://localhost:8000/api/user/tasks/ \
  -H "Authorization: Bearer <token>"

# Response for user with assigned tasks:
[
  {
    "id": 1,
    "title": "Create Wireframes",
    "description": "Design wireframes for homepage",
    "status": "todo",
    "priority": "high",
    "assignee": 2,
    "milestone": 1,
    "logged_hours": "0.00"
  }
]

# Response for admin/manager (empty list):
[]
```

**Example**:
```bash
# Create Task
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Create Wireframes",
    "description": "Design wireframes for homepage and product pages",
    "milestone": 1,
    "assignee": 2,
    "priority": "high",
    "status": "todo"
  }'

# List Tasks
curl -X GET http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer <token>"

# Filter Tasks
curl -X GET "http://localhost:8000/api/tasks/?status=todo&assignee=2" \
  -H "Authorization: Bearer <token>"
```

#### Task Details
**GET/PUT/DELETE** `/api/tasks/{id}/`
- **Description**: Get, update, or delete a task
- **Authentication**: Required
- **Permissions**: Task assignee, manager, or admin
- **Note**: Update operations allow partial updates (fields are optional)

**Example**:
```bash
# Get Task
curl -X GET http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer <token>"

# Update Task
curl -X PUT http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Task Title",
    "status": "in_progress",
    "priority": "medium"
  }'

# Delete Task
curl -X DELETE http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer <token>"
```

#### Log Time to Task
**POST** `/api/tasks/{id}/log_time/`
- **Description**: Log hours worked on a task
- **Authentication**: Required
- **Permissions**: Task assignee, manager, or admin
- **Required Fields**:
  - `hours` (decimal)
- **Response Fields**: `task_id`, `logged_hours`

**Example**:
```bash
curl -X POST http://localhost:8000/api/tasks/1/log_time/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "hours": 4.5
  }'
```

### 6. Comment Management

#### List/Create Comments
**GET/POST** `/api/comments/`
- **Description**: List comments (filtered by role) or create new comment
- **Authentication**: Required
- **Required Fields** (for POST):
  - `content` (string)
  - `task` (integer: task ID)
  - `user` (integer: user ID)
- **Response Fields**: `id`, `content`, `timestamp`, `task`, `user`
- **Permissions**: 
  - GET: All authenticated users (filtered by role)
  - POST: All authenticated users
- **Note**: Users see comments from tasks they're assigned to or projects they own/are members of, admins/managers see all comments

**Example**:
```bash
# Create Comment
curl -X POST http://localhost:8000/api/comments/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Wireframes look great! Ready to move to development phase.",
    "task": 1,
    "user": 2
  }'

# List Comments
curl -X GET http://localhost:8000/api/comments/ \
  -H "Authorization: Bearer <token>"
```

#### Comment Details
**GET/PUT/DELETE** `/api/comments/{id}/`
- **Description**: Get, update, or delete a comment
- **Authentication**: Required
- **Permissions**: Comment author, manager, or admin
- **Note**: Update operations allow partial updates (fields are optional)

**Example**:
```bash
# Get Comment
curl -X GET http://localhost:8000/api/comments/1/ \
  -H "Authorization: Bearer <token>"

# Update Comment
curl -X PUT http://localhost:8000/api/comments/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated comment content"
  }'

# Delete Comment
curl -X DELETE http://localhost:8000/api/comments/1/ \
  -H "Authorization: Bearer <token>"
```

### 7. Attachment Management

#### List/Create Attachments
**GET/POST** `/api/attachments/`
- **Description**: List attachments (filtered by role) or create new attachment
- **Authentication**: Required
- **Required Fields** (for POST):
  - `file` (file upload)
  - `task` (integer: task ID)
- **Response Fields**: `id`, `file`, `task`
- **Permissions**: 
  - GET: All authenticated users (filtered by role)
  - POST: All authenticated users
- **Note**: Users see attachments from tasks they're assigned to or projects they own/are members of, admins/managers see all attachments

**Example**:
```bash
# Create Attachment
curl -X POST http://localhost:8000/api/attachments/ \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/to/document.pdf" \
  -F "task=1"

# List Attachments
curl -X GET http://localhost:8000/api/attachments/ \
  -H "Authorization: Bearer <token>"
```

#### Attachment Details
**GET/PUT/DELETE** `/api/attachments/{id}/`
- **Description**: Get, update, or delete an attachment
- **Authentication**: Required
- **Permissions**: Task assignee, manager, or admin
- **Note**: Update operations allow partial updates (fields are optional)

**Example**:
```bash
# Get Attachment
curl -X GET http://localhost:8000/api/attachments/1/ \
  -H "Authorization: Bearer <token>"

# Update Attachment
curl -X PUT http://localhost:8000/api/attachments/1/ \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/to/new_document.pdf"

# Delete Attachment
curl -X DELETE http://localhost:8000/api/attachments/1/ \
  -H "Authorization: Bearer <token>"
```

## Response Status Codes

- **200**: Success
- **201**: Created
- **204**: No Content (for DELETE operations)
- **400**: Bad Request (validation error)
- **401**: Unauthorized (authentication required)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **500**: Internal Server Error

## Examples

### Complete Workflow Example

```bash
# 1. Register an admin
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_user",
    "email": "admin@example.com",
    "password": "securepass123",
    "password2": "securepass123",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin"
  }'

# 2. Login to get token
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_user",
    "password": "securepass123"
  }'

# 3. Create a regular user
curl -X POST http://localhost:8000/api/users/create/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "developer_jane",
    "email": "jane@example.com",
    "password": "securepass123",
    "password2": "securepass123",
    "first_name": "Jane",
    "last_name": "Developer",
    "role": "user"
  }'

# 4. Create a project
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "E-commerce Platform",
    "description": "Build a modern e-commerce platform",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'

# 5. Add user to project
curl -X POST http://localhost:8000/api/projects/1/members/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2
  }'

# 6. Create a milestone
curl -X POST http://localhost:8000/api/milestones/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Frontend Development",
    "due_date": "2024-06-30",
    "project": 1
  }'

# 7. Create a task
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement User Authentication",
    "description": "Create login and registration system",
    "milestone": 1,
    "assignee": 2,
    "priority": "high",
    "status": "todo"
  }'

# 8. Log time to task
curl -X POST http://localhost:8000/api/tasks/1/log_time/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "hours": 8.0
  }'

# 9. Add a comment
curl -X POST http://localhost:8000/api/comments/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Authentication system completed successfully!",
    "task": 1,
    "user": 2
  }'

# 10. Check project progress
curl -X GET http://localhost:8000/api/projects/1/progress/ \
  -H "Authorization: Bearer <admin_token>"

# 11. Check total hours
curl -X GET http://localhost:8000/api/projects/1/total_hours/ \
  -H "Authorization: Bearer <admin_token>"
```

## Design Justifications

1. **JWT Authentication**: Secure, stateless authentication suitable for API-first applications
2. **Role-Based Access Control**: Granular permissions based on user roles for security
3. **Filtered Queries**: Users only see data they're authorized to access
4. **Health Check**: Essential for monitoring and load balancers
5. **Comprehensive CRUD**: Full create, read, update, delete operations for all entities
6. **Time Logging**: Built-in time tracking for project management and billing
7. **Progress Tracking**: Automatic calculation of project completion percentages
8. **File Attachments**: Support for file uploads to tasks for document management
9. **Comments System**: Communication and collaboration features for team coordination
10. **Flexible Permissions**: Different access levels for different user roles
11. **RESTful Design**: Follows REST conventions for clarity and interoperability
12. **Error Handling**: Consistent error responses for better client integration
13. **Query Filtering**: Support for filtering tasks by status and assignee
14. **Scalable Architecture**: Designed to handle multiple users and projects efficiently
15. **Project Member Management**: Advanced team collaboration with role-based constraints
16. **Partial Updates**: Support for partial updates in PUT operations for better UX

## API Versioning
This is version 1.0 of the API. Future versions will maintain backward compatibility where possible.

## Rate Limiting
Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Security Considerations
- All sensitive endpoints require JWT authentication
- Role-based access control prevents unauthorized access
- Password validation ensures strong passwords
- JWT tokens have expiration times for security
- Object-level permissions ensure data isolation
- Project member constraints prevent privilege escalation
- Validation occurs at both model and serializer levels

## Support
For API support and questions, please refer to the project documentation or contact the development team.
