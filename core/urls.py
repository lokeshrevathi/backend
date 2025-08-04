from django.urls import path
from .views import (
    UserRegistrationView, UserLoginView, UserDetailView, UserCreateView,
    ProjectListCreateView, ProjectDetailView, ProjectMemberListView, ProjectMemberDetailView, AvailableUsersListView,
    MilestoneListCreateView, MilestoneDetailView,
    TaskListCreateView, TaskDetailView, UserTasksView, LogTimeView, ProjectHoursView, ProjectProgressView,
    CommentListCreateView, CommentDetailView,
    AttachmentListCreateView, AttachmentDetailView
)

urlpatterns = [
    # Authentication & User Management
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    
    # Project Management
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:pk>/progress/', ProjectProgressView.as_view(), name='project-progress'),
    path('projects/<int:pk>/total_hours/', ProjectHoursView.as_view(), name='project-hours'),
    
    # Project Member Management
    path('projects/<int:project_id>/members/', ProjectMemberListView.as_view(), name='project-members'),
    path('projects/<int:project_id>/members/<int:user_id>/', ProjectMemberDetailView.as_view(), name='project-member-detail'),
    path('projects/<int:project_id>/available-users/', AvailableUsersListView.as_view(), name='available-users'),
    
    # Milestone Management
    path('milestones/', MilestoneListCreateView.as_view(), name='milestone-list-create'),
    path('milestones/<int:pk>/', MilestoneDetailView.as_view(), name='milestone-detail'),
    
    # Task Management
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('user/tasks/', UserTasksView.as_view(), name='user-tasks'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/log_time/', LogTimeView.as_view(), name='log-time'),
    
    # Comment Management
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    
    # Attachment Management
    path('attachments/', AttachmentListCreateView.as_view(), name='attachment-list-create'),
    path('attachments/<int:pk>/', AttachmentDetailView.as_view(), name='attachment-detail'),
]
