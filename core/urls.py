from django.urls import path
from .views import (
    RegisterView, CustomTokenObtainPairView, UserDetailView,
    ProjectListCreateView, ProjectDetailView,
    MilestoneListCreateView, MilestoneDetailView,
    TaskListCreateView, TaskDetailView,
    CommentListCreateView, CommentDetailView,
    AttachmentListCreateView, AttachmentDetailView,
    LogTimeView, ProjectHoursView, ProjectProgressView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # JWT login endpoint (returns access/refresh tokens)
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserDetailView.as_view(), name='user_detail'),

    # Log time against a task
    path('tasks/<int:pk>/log_time/', LogTimeView.as_view(), name='task-log-time'),
    # Total hours per project
    path('projects/<int:pk>/total_hours/', ProjectHoursView.as_view(), name='project-total-hours'),
    # Progress percentage per project
    path('projects/<int:pk>/progress/', ProjectProgressView.as_view(), name='project-progress'),

    # Project
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),

    # Milestone
    path('milestones/', MilestoneListCreateView.as_view(), name='milestone-list-create'),
    path('milestones/<int:pk>/', MilestoneDetailView.as_view(), name='milestone-detail'),

    # Task
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),

    # Comment
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),

    # Attachment
    path('attachments/', AttachmentListCreateView.as_view(), name='attachment-list-create'),
    path('attachments/<int:pk>/', AttachmentDetailView.as_view(), name='attachment-detail'),
]
