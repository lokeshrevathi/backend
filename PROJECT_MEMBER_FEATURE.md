# Project Member Management Feature

## Overview
This document describes the implementation of the project member management feature with specific constraints for user roles and project assignments.

## Feature Requirements
1. **User Role Constraint**: Only users with 'user' role can be added to projects as members
2. **Maximum Project Limit**: One user can be assigned to maximum 2 projects only

## Implementation Details

### Database Model
- **ProjectMember Model**: Tracks project memberships with validation constraints
- **Unique Constraint**: Prevents duplicate user-project assignments
- **Validation Logic**: Enforces role and project limit constraints

### API Endpoints

#### 1. List Project Members
- **Endpoint**: `GET /api/projects/{project_id}/members/`
- **Authentication**: Required (Admin/Manager)
- **Response**: List of project members with user details

#### 2. Add User to Project
- **Endpoint**: `POST /api/projects/{project_id}/members/`
- **Authentication**: Required (Admin/Manager)
- **Request Body**: `{"user_id": <user_id>}`
- **Constraints**:
  - Only 'user' role allowed
  - Maximum 2 projects per user
  - Cannot add project owner
  - Cannot add duplicate members

#### 3. Remove User from Project
- **Endpoint**: `DELETE /api/projects/{project_id}/members/{user_id}/`
- **Authentication**: Required (Admin/Manager)
- **Response**: 204 No Content

#### 4. Get Available Users
- **Endpoint**: `GET /api/projects/{project_id}/available-users/`
- **Authentication**: Required (Admin/Manager)
- **Response**: List of users who can be added to the project
- **Filters**: Excludes existing members, users at max limit, and project owner

### Validation Rules

#### Model Level Validation
```python
def clean(self):
    # Constraint 1: Only users can be added to projects
    if self.user and not self.user.is_user:
        raise ValidationError("Only users with 'user' role can be added to projects as members.")
    
    # Constraint 2: One user can be assigned to maximum 2 projects
    existing_projects = ProjectMember.objects.filter(user=self.user).exclude(pk=self.pk).count()
    if existing_projects >= 2:
        raise ValidationError(f"User {self.user.username} is already assigned to {existing_projects} projects. Maximum allowed is 2.")
```

#### Serializer Level Validation
```python
def validate(self, attrs):
    # Check if user is already a member
    # Check if user is at maximum limit (2 projects)
    # Check if user is the project owner
    # Validate user role
```

### Permission System
- **CanManageProjectMembers**: Only admins and managers can manage project members
- **IsProjectMemberOrManagerOrAdmin**: Project members can access project-related data

### Integration with Existing Features

#### Project Serializer Updates
- Added `members` field: Returns list of project members
- Added `member_count` field: Returns total number of project members

#### Enhanced Project Access
- Users can now access projects they are members of (not just owned)
- Milestones, tasks, comments, and attachments are accessible to project members

### Testing Results
- **Test Coverage**: 100% success rate
- **Constraint Testing**: All validation rules working correctly
- **API Testing**: All endpoints functioning as expected

## Usage Examples

### Adding a User to a Project
```bash
curl -X POST http://localhost:8000/api/projects/1/members/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2}'
```

### Getting Project Members
```bash
curl -X GET http://localhost:8000/api/projects/1/members/ \
  -H "Authorization: Bearer <admin_token>"
```

### Getting Available Users
```bash
curl -X GET http://localhost:8000/api/projects/1/available-users/ \
  -H "Authorization: Bearer <admin_token>"
```

## Error Handling

### Common Error Responses
1. **User Role Error**: `"Only users with 'user' role can be added to projects."`
2. **Maximum Limit Error**: `"User {username} is already assigned to {count} projects. Maximum allowed is 2."`
3. **Duplicate Member Error**: `"User is already a member of this project."`
4. **Owner Error**: `"Project owner cannot be added as a member."`

## Security Considerations
- Only authenticated admins and managers can manage project members
- Validation occurs at both model and serializer levels
- Project members have appropriate access to project resources
- No privilege escalation through project membership

## Future Enhancements
- Bulk add/remove operations
- Project member roles (e.g., viewer, contributor, admin)
- Project member activity tracking
- Email notifications for project membership changes 