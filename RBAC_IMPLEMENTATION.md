# Role-Based Access Control (RBAC) Implementation

## Overview
This document describes the implementation of role-based access control (RBAC) in the Project Management Dashboard API. The system now supports three user roles: `admin`, `manager`, and `user`, each with specific permissions and access levels.

## User Roles

### 1. Admin Role
- **Permissions**:
  - Create users and managers
  - Access all projects, milestones, tasks, comments, and attachments
  - Create projects, milestones, and tasks
  - Assign users to tasks
  - Assign tasks to users
  - Full CRUD operations on all resources

### 2. Manager Role
- **Permissions**:
  - Create projects, milestones, and tasks
  - Access all projects, milestones, tasks, comments, and attachments
  - Assign users to tasks
  - Assign tasks to users
  - Full CRUD operations on all resources

### 3. User Role
- **Permissions**:
  - Create projects, milestones, and tasks
  - Access only their assigned tasks
  - Access only their owned projects
  - Create comments on their tasks
  - Upload attachments to their tasks
  - Log time to their assigned tasks

## Implementation Details

### 1. User Model Changes

**File**: `core/models.py`

```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        help_text='User role in the system'
    )
    
    # Helper properties
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_manager(self):
        return self.role == 'manager'
    
    @property
    def is_user(self):
        return self.role == 'user'
    
    # Permission methods
    def can_create_users(self):
        return self.is_admin
    
    def can_create_managers(self):
        return self.is_admin
    
    def can_create_projects(self):
        return True  # All authenticated users can create projects
    
    def can_assign_users(self):
        return self.is_admin or self.is_manager
    
    def can_assign_tasks(self):
        return self.is_admin or self.is_manager
```

### 2. Custom Permission Classes

**File**: `core/permissions.py`

#### Key Permission Classes:

1. **IsAdminUser**: Only allows admin users
2. **IsManagerOrAdmin**: Allows managers and admins
3. **CanCreateUsers**: Only admins can create users
4. **CanCreateProjects**: All authenticated users can create projects
5. **CanAssignUsers**: Only managers and admins can assign users
6. **CanAssignTasks**: Only managers and admins can assign tasks
7. **IsOwnerOrManagerOrAdmin**: Object-level permissions for owners, managers, and admins
8. **IsTaskAssigneeOrManagerOrAdmin**: Task-specific permissions
9. **IsProjectOwnerOrManagerOrAdmin**: Project-specific permissions

### 3. Serializer Updates

**File**: `core/serializers.py`

#### UserRegistrationSerializer
- Added role field with validation
- Public registration defaults to 'user' role
- Only admins can create managers and admins

#### UserCreateSerializer
- Admin-only endpoint for creating users with specific roles
- Role validation to prevent unauthorized role creation

### 4. View Updates

**File**: `core/views.py`

#### Key Changes:
- Updated all views to use appropriate permission classes
- Added role-based queryset filtering
- Implemented proper access control for all endpoints

#### New Endpoint:
- **UserCreateView**: Admin-only endpoint for creating users with specific roles

### 5. URL Configuration

**File**: `core/urls.py`

Added new endpoint:
```python
path('users/create/', UserCreateView.as_view(), name='user-create'),
```

## Permission Matrix

| Action | Admin | Manager | User |
|--------|-------|---------|------|
| Create Users/Managers | ✅ | ❌ | ❌ |
| Create Projects | ✅ | ✅ | ✅ |
| Create Milestones | ✅ | ✅ | ✅ |
| Create Tasks | ✅ | ✅ | ✅ |
| Assign Users to Tasks | ✅ | ✅ | ❌ |
| Assign Tasks | ✅ | ✅ | ❌ |
| Access All Projects | ✅ | ✅ | ❌ |
| Access All Tasks | ✅ | ✅ | ❌ |
| Access Own Projects | ✅ | ✅ | ✅ |
| Access Assigned Tasks | ✅ | ✅ | ✅ |
| Create Comments | ✅ | ✅ | ✅ |
| Upload Attachments | ✅ | ✅ | ✅ |
| Log Time | ✅ | ✅ | ✅ |

## API Endpoints with RBAC

### Public Endpoints (No Authentication Required)
- `POST /api/register/` - User registration (defaults to 'user' role)
- `POST /api/login/` - User login
- `POST /api/token/refresh/` - Token refresh
- `GET /health/` - Health check

### Admin-Only Endpoints
- `POST /api/users/create/` - Create users with specific roles

### Role-Based Endpoints
All other endpoints have role-based access control:

#### Projects
- **List/Create**: All authenticated users
- **Detail/Update/Delete**: Project owner, manager, or admin
- **Progress/Total Hours**: Project owner, manager, or admin

#### Milestones
- **List/Create**: All authenticated users
- **Detail/Update/Delete**: Project owner, manager, or admin

#### Tasks
- **List**: Filtered by role (all for managers/admins, assigned only for users)
- **Create**: All authenticated users
- **Detail/Update/Delete**: Task assignee, manager, or admin
- **Log Time**: Task assignee, manager, or admin

#### Comments
- **List**: Filtered by role
- **Create**: All authenticated users
- **Detail/Update/Delete**: Comment author, manager, or admin

#### Attachments
- **List**: Filtered by role
- **Create**: All authenticated users
- **Detail/Update/Delete**: Task assignee, manager, or admin

## Database Migration

The role field was added to the User model with migration:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Testing

### Test Scripts Created:
1. **test_rbac.py** - Basic RBAC functionality testing
2. **test_rbac_final.py** - Comprehensive RBAC testing with unique usernames

### Test Coverage:
- ✅ User registration with role assignment
- ✅ Role-based permission enforcement
- ✅ Role escalation prevention
- ✅ API access restrictions
- ✅ Project, milestone, and task creation permissions
- ✅ User creation permissions

## Security Features

### 1. Role Escalation Prevention
- Public registration only allows 'user' role
- Only admins can create managers and admins
- Role validation in serializers

### 2. Object-Level Permissions
- Users can only access their own projects
- Users can only access their assigned tasks
- Managers and admins have broader access

### 3. Query Filtering
- Database queries are filtered by role
- Users only see data they're authorized to access

### 4. JWT Authentication
- Secure token-based authentication
- Role information included in user details

## Usage Examples

### Creating an Admin User
```bash
# First, create an admin user directly in the database or via Django admin
# Then use the admin token to create other users

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

### Regular User Registration
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "password2": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

## Benefits

1. **Security**: Granular access control prevents unauthorized access
2. **Scalability**: Role-based system can easily accommodate new roles
3. **Maintainability**: Clear separation of concerns and permissions
4. **User Experience**: Users only see relevant data
5. **Compliance**: Supports organizational hierarchy and access policies

## Future Enhancements

1. **Role Hierarchy**: Implement role inheritance
2. **Permission Groups**: Allow custom permission groups
3. **Audit Logging**: Track permission changes and access
4. **Dynamic Permissions**: Runtime permission modification
5. **Multi-tenancy**: Support for multiple organizations

## Conclusion

The RBAC implementation provides a robust, secure, and scalable access control system for the Project Management Dashboard. It ensures that users can only access and modify data they're authorized to work with, while providing the flexibility needed for different organizational roles and responsibilities. 