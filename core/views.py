
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import User, Project, Milestone, Task, Comment, Attachment, ProjectMember
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserDetailSerializer, UserCreateSerializer,
    ProjectSerializer, MilestoneSerializer, TaskSerializer, CommentSerializer, AttachmentSerializer,
    ProjectMemberSerializer, ProjectMemberListSerializer
)
from .permissions import (
    IsAdminUser, IsManagerOrAdmin, CanCreateUsers, CanCreateProjects, CanAssignUsers, CanAssignTasks,
    IsOwnerOrManagerOrAdmin, IsTaskAssigneeOrManagerOrAdmin, IsProjectOwnerOrManagerOrAdmin,
    IsMilestoneProjectOwnerOrManagerOrAdmin, CanManageProjectMembers, IsProjectMemberOrManagerOrAdmin
)
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from django.db import models

# Authentication Views
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = []

class UserLoginView(generics.CreateAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [IsAuthenticated, CanCreateUsers]

# Project Views
class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return Project.objects.all()
        else:
            # Users see projects they own or are members of
            return Project.objects.filter(
                Q(owner=user) | Q(projectmembership__user=user)
            ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrManagerOrAdmin]

# Project Member Views
class ProjectMemberListView(generics.ListCreateAPIView):
    serializer_class = ProjectMemberSerializer
    permission_classes = [IsAuthenticated, CanManageProjectMembers]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        return ProjectMember.objects.filter(project=project)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project_id'] = self.kwargs.get('project_id')
        return context

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        serializer.save(project=project)

class ProjectMemberDetailView(generics.DestroyAPIView):
    queryset = ProjectMember.objects.all()
    serializer_class = ProjectMemberSerializer
    permission_classes = [IsAuthenticated, CanManageProjectMembers]

    def get_object(self):
        project_id = self.kwargs.get('project_id')
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(ProjectMember, project_id=project_id, user_id=user_id)

class AvailableUsersListView(generics.ListAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated, CanManageProjectMembers]

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

# Milestone Views
class MilestoneListCreateView(generics.ListCreateAPIView):
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return Milestone.objects.all()
        else:
            # Users see milestones of projects they own or are members of
            return Milestone.objects.filter(
                Q(project__owner=user) | Q(project__projectmembership__user=user)
            ).distinct()

class MilestoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated, IsMilestoneProjectOwnerOrManagerOrAdmin]

# Task Views
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return Task.objects.all()
        else:
            # Users see tasks assigned to them or from projects they own/are members of
            return Task.objects.filter(
                Q(assignee=user) | 
                Q(milestone__project__owner=user) | 
                Q(milestone__project__projectmembership__user=user)
            ).distinct()

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskAssigneeOrManagerOrAdmin]

class UserTasksView(generics.ListAPIView):
    """Get tasks assigned to the authenticated user (user role only)"""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Only users with 'user' role can access this endpoint
        if not user.is_user:
            return Task.objects.none()
        
        # Return only tasks directly assigned to the user
        return Task.objects.filter(assignee=user)

class LogTimeView(generics.CreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=self.kwargs['pk'])
        hours = request.data.get('hours', 0)
        
        if hours <= 0:
            return Response(
                {'error': 'Hours must be greater than 0'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.logged_hours += float(hours)
        task.save()
        
        return Response({
            'task_id': task.id,
            'logged_hours': task.logged_hours
        })

class ProjectHoursView(generics.RetrieveAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        total_hours = sum(task.logged_hours for task in project.milestones.all().values_list('tasks__logged_hours', flat=True))
        
        return Response({
            'project_id': project.id,
            'total_hours': total_hours
        })

class ProjectProgressView(generics.RetrieveAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        tasks = Task.objects.filter(milestone__project=project)
        
        if not tasks:
            progress = 0
        else:
            completed_tasks = tasks.filter(status='done').count()
            progress = (completed_tasks / tasks.count()) * 100
        
        return Response({
            'project_id': project.id,
            'progress_percent': round(progress, 2)
        })

# Comment Views
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return Comment.objects.all()
        else:
            # Users see comments from tasks they're assigned to or projects they own/are members of
            return Comment.objects.filter(
                Q(task__assignee=user) | 
                Q(task__milestone__project__owner=user) | 
                Q(task__milestone__project__projectmembership__user=user)
            ).distinct()

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrManagerOrAdmin]

# Attachment Views
class AttachmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return Attachment.objects.all()
        else:
            # Users see attachments from tasks they're assigned to or projects they own/are members of
            return Attachment.objects.filter(
                Q(task__assignee=user) | 
                Q(task__milestone__project__owner=user) | 
                Q(task__milestone__project__projectmembership__user=user)
            ).distinct()

class AttachmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated, IsProjectMemberOrManagerOrAdmin]
