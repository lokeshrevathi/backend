# Available Users for Project Assignment Feature

## Overview
The "Get Available Users for Project Assignment" feature provides a smart filtering mechanism to identify users who can be added to projects based on specific constraints. This feature ensures efficient project member management by automatically excluding users who are not eligible for assignment.

## Feature Requirements

### Primary Constraint
**Users already assigned to 2 projects should not be fetched**

### Additional Constraints
1. **Role-based filtering**: Only users with 'user' role are included
2. **Existing membership**: Users already members of the target project are excluded
3. **Project ownership**: Project owner is excluded from available users
4. **Maximum project limit**: Users at maximum limit (2 projects) are excluded

## Implementation Details

### API Endpoint
- **URL**: `GET /api/projects/{project_id}/available-users/`
- **Authentication**: Required (Admin/Manager only)
- **Permission**: `CanManageProjectMembers`

### Database Query Logic
The implementation uses Django ORM with optimized queries:

```python
def get_queryset(self):
    """Get users who can be added to projects (only 'user' role and not at max limit)"""
    project_id = self.kwargs.get('project_id')
    project = get_object_or_404(Project, id=project_id)
    
    # Get users with 'user' role who are not already members of this project
    existing_members = ProjectMember.objects.filter(project=project).values_list('user_id', flat=True)
    
    # Get users who are at max limit (2 projects)
    users_at_max = ProjectMember.objects.values('user').annotate(
        project_count=models.Count('project')
    ).filter(project_count__gte=2).values_list('user_id', flat=True)
    
    return User.objects.filter(
        role='user'
    ).exclude(
        id__in=existing_members
    ).exclude(
        id__in=users_at_max
    ).exclude(
        id=project.owner.id  # Exclude project owner
    )
```

### Query Optimization
- Uses `values_list` for efficient ID extraction
- Uses `annotate` with `Count` for project counting
- Single database query with multiple `exclude` clauses
- Indexed lookups on user ID and project relationships

## Constraint Validation

### 1. Role Constraint
```python
# Only users with 'user' role
User.objects.filter(role='user')
```
- **Purpose**: Ensures only regular users can be assigned to projects
- **Excludes**: Admin and Manager roles

### 2. Existing Membership Constraint
```python
# Users already members of this project
existing_members = ProjectMember.objects.filter(project=project).values_list('user_id', flat=True)
User.objects.exclude(id__in=existing_members)
```
- **Purpose**: Prevents duplicate project memberships
- **Excludes**: Users already assigned to the target project

### 3. Maximum Project Limit Constraint
```python
# Users at maximum limit (2 projects)
users_at_max = ProjectMember.objects.values('user').annotate(
    project_count=models.Count('project')
).filter(project_count__gte=2).values_list('user_id', flat=True)
User.objects.exclude(id__in=users_at_max)
```
- **Purpose**: Enforces the 2-project limit per user
- **Excludes**: Users already assigned to 2 or more projects

### 4. Project Owner Constraint
```python
# Exclude project owner
User.objects.exclude(id=project.owner.id)
```
- **Purpose**: Project owner cannot be added as a member
- **Excludes**: The user who owns the project

## Usage Examples

### Basic Usage
```bash
# Get available users for project assignment
curl -X GET http://localhost:8000/api/projects/1/available-users/ \
  -H "Authorization: Bearer <admin_token>"
```

### Response Format
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

## Testing Scenarios

### Scenario 1: Initial State
- **Setup**: 4 users with 'user' role, 1 project
- **Expected**: All 4 users available
- **Result**: ✅ All users returned

### Scenario 2: User Already Member
- **Setup**: User1 is member of Project1
- **Expected**: User1 excluded from available users
- **Result**: ✅ User1 correctly excluded

### Scenario 3: User at Maximum Limit
- **Setup**: User1 assigned to 2 projects
- **Expected**: User1 excluded from available users for new projects
- **Result**: ✅ User1 correctly excluded due to 2-project limit

### Scenario 4: Multiple Users at Limit
- **Setup**: User1 and User2 both at 2-project limit
- **Expected**: Both users excluded from available users
- **Result**: ✅ Both users correctly excluded

### Scenario 5: Project Owner Exclusion
- **Setup**: Admin owns Project1
- **Expected**: Admin excluded from available users
- **Result**: ✅ Project owner correctly excluded

## Integration with Project Member Management

### Workflow Integration
1. **Admin/Manager** accesses project member management
2. **Available Users** endpoint provides filtered user list
3. **User Selection** from available users only
4. **Assignment** using project member creation endpoint
5. **Validation** ensures constraints are maintained

### Error Handling
- **404**: Project not found
- **403**: Insufficient permissions (not admin/manager)
- **401**: Authentication required

## Performance Considerations

### Database Optimization
- **Indexes**: User role, ProjectMember relationships
- **Query Efficiency**: Single query with multiple exclusions
- **Caching**: Consider Redis caching for large user bases

### Scalability
- **Pagination**: Consider adding pagination for large user lists
- **Search**: Consider adding search functionality
- **Filtering**: Consider additional filters (department, skills, etc.)

## Security Features

### Authentication & Authorization
- **JWT Authentication**: Required for all requests
- **Role-based Access**: Only Admin/Manager can access
- **Project-level Permissions**: Must have project management rights

### Data Protection
- **User Privacy**: Only necessary user fields returned
- **Project Isolation**: Users can only see available users for their projects
- **Audit Trail**: All access logged for security monitoring

## Future Enhancements

### Potential Improvements
1. **Advanced Filtering**: Filter by skills, experience, availability
2. **Bulk Operations**: Add multiple users at once
3. **Temporary Assignments**: Support for temporary project memberships
4. **Workload Balancing**: Consider current workload in availability
5. **Notification System**: Notify users when added to projects

### API Extensions
1. **Search Parameters**: Add search by name, email, skills
2. **Sorting Options**: Sort by name, experience, availability
3. **Pagination Support**: Handle large user lists efficiently
4. **Caching Headers**: Implement proper caching strategies

## Troubleshooting

### Common Issues

#### Issue: No users returned
**Possible Causes**:
- All users already at 2-project limit
- All users already members of the project
- No users with 'user' role exist
- Project owner is the only user

**Solutions**:
- Check user project assignments
- Verify user roles
- Create additional users if needed

#### Issue: Unexpected users excluded
**Possible Causes**:
- User recently assigned to 2 projects
- User role changed from 'user' to 'admin'/'manager'
- Database inconsistency

**Solutions**:
- Verify user project assignments
- Check user role
- Refresh data or restart application

#### Issue: Performance issues
**Possible Causes**:
- Large number of users
- Inefficient database queries
- Missing database indexes

**Solutions**:
- Add database indexes
- Implement pagination
- Consider caching strategies

## Conclusion

The Available Users for Project Assignment feature provides a robust, constraint-aware system for project member management. The implementation ensures:

- ✅ **Constraint Enforcement**: 2-project limit strictly enforced
- ✅ **Performance**: Optimized database queries
- ✅ **Security**: Proper authentication and authorization
- ✅ **Scalability**: Ready for future enhancements
- ✅ **Reliability**: Comprehensive error handling

This feature is essential for maintaining project management efficiency and ensuring fair workload distribution among team members. 