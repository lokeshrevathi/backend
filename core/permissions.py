from rest_framework import permissions
from .models import User

class IsAdminUser(permissions.BasePermission):
    """
    Allow access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin

class IsManagerOrAdmin(permissions.BasePermission):
    """
    Allow access only to manager or admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.is_manager or request.user.is_admin)

class CanCreateUsers(permissions.BasePermission):
    """
    Allow access only to users who can create other users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.can_create_users()

class CanCreateProjects(permissions.BasePermission):
    """
    Allow access only to users who can create projects.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.can_create_projects()

class CanAssignUsers(permissions.BasePermission):
    """
    Allow access only to users who can assign users to tasks.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.can_assign_users()

class CanAssignTasks(permissions.BasePermission):
    """
    Allow access only to users who can assign tasks.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.can_assign_tasks()

class CanManageProjectMembers(permissions.BasePermission):
    """
    Allow access only to users who can manage project members.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.can_manage_project_members()

class IsOwnerOrManagerOrAdmin(permissions.BasePermission):
    """
    Allow access only to the owner, manager, or admin.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is admin or manager
        if request.user.is_admin or request.user.is_manager:
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False

class IsTaskAssigneeOrManagerOrAdmin(permissions.BasePermission):
    """
    Allow access only to the task assignee, manager, or admin.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is admin or manager
        if request.user.is_admin or request.user.is_manager:
            return True
        
        # Check if user is the assignee
        if hasattr(obj, 'assignee'):
            return obj.assignee == request.user
        
        return False

class IsProjectOwnerOrManagerOrAdmin(permissions.BasePermission):
    """
    Allow access only to the project owner, manager, or admin.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is admin or manager
        if request.user.is_admin or request.user.is_manager:
            return True
        
        # Check if user is the project owner
        if hasattr(obj, 'project') and hasattr(obj.project, 'owner'):
            return obj.project.owner == request.user
        
        return False

class IsMilestoneProjectOwnerOrManagerOrAdmin(permissions.BasePermission):
    """
    Allow access only to the milestone's project owner, manager, or admin.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is admin or manager
        if request.user.is_admin or request.user.is_manager:
            return True
        
        # Check if user is the project owner
        if hasattr(obj, 'project') and hasattr(obj.project, 'owner'):
            return obj.project.owner == request.user
        
        return False

class IsProjectMemberOrManagerOrAdmin(permissions.BasePermission):
    """
    Allow access only to project members, managers, or admins.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is admin or manager
        if request.user.is_admin or request.user.is_manager:
            return True
        
        # Check if user is the project owner
        if hasattr(obj, 'project') and hasattr(obj.project, 'owner'):
            if obj.project.owner == request.user:
                return True
        
        # Check if user is a project member
        if hasattr(obj, 'project'):
            from .models import ProjectMember
            return ProjectMember.objects.filter(project=obj.project, user=request.user).exists()
        
        return False 