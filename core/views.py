
from rest_framework import generics, status, views
from rest_framework.permissions import BasePermission
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserDetailSerializer,
    ProjectSerializer, MilestoneSerializer, TaskSerializer, CommentSerializer, AttachmentSerializer
)


from .PMLogger import PMLogger
import uuid

trace_logger = PMLogger()

# Log time against a task
class LogTimeView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        trace_id = request.headers.get('X-Trace-Id', str(uuid.uuid4()))
        try:
            task = Task.objects.get(pk=pk, milestone__project__owner=request.user)
        except Task.DoesNotExist:
            trace_logger.info(f"Task {pk} not found for user {request.user.id}", trace_id)
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        hours = request.data.get('hours')
        try:
            from decimal import Decimal
            hours = Decimal(str(hours))
        except (TypeError, ValueError, ImportError):
            trace_logger.info(f"Invalid hours value: {hours}", trace_id)
            return Response({'detail': 'Invalid hours.'}, status=status.HTTP_400_BAD_REQUEST)
        task.logged_hours += hours
        task.save()
        trace_logger.info(f"Logged {hours} hours to task {task.id} by user {request.user.id}", trace_id)
        return Response({'task_id': task.id, 'logged_hours': float(task.logged_hours)}, status=status.HTTP_200_OK)

# Total hours per project
class ProjectHoursView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        trace_id = request.headers.get('X-Trace-Id', str(uuid.uuid4()))
        try:
            project = Project.objects.get(pk=pk, owner=request.user)
        except Project.DoesNotExist:
            trace_logger.info(f"Project {pk} not found for user {request.user.id}", trace_id)
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        total_hours = Task.objects.filter(milestone__project=project).aggregate(total=models.Sum('logged_hours'))['total'] or 0
        trace_logger.info(f"Total hours for project {project.id}: {total_hours}", trace_id)
        return Response({'project_id': project.id, 'total_hours': float(total_hours)}, status=status.HTTP_200_OK)

# Progress percentage per project
class ProjectProgressView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        trace_id = request.headers.get('X-Trace-Id', str(uuid.uuid4()))
        try:
            project = Project.objects.get(pk=pk, owner=request.user)
        except Project.DoesNotExist:
            trace_logger.info(f"Project {pk} not found for user {request.user.id}", trace_id)
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        tasks = Task.objects.filter(milestone__project=project)
        total = tasks.count()
        if total == 0:
            percent = 0.0
        else:
            done = tasks.filter(status='done').count()
            percent = (done / total) * 100
        trace_logger.info(f"Progress for project {project.id}: {percent}%", trace_id)
        return Response({'project_id': project.id, 'progress_percent': round(percent, 2)}, status=status.HTTP_200_OK)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = TokenObtainPairSerializer

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user


# Custom permission: Only allow users to access/modify their own objects
class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # For Project, Milestone, Task, Comment, Attachment
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'assignee'):
            return obj.assignee == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False

from .models import Project, Milestone, Task, Comment, Attachment
from django.db import models

class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

# Milestone CRUD
class MilestoneListCreateView(generics.ListCreateAPIView):
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Milestone.objects.filter(project__owner=self.request.user)

class MilestoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

# Task CRUD
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'assignee']

    def get_queryset(self):
        return Task.objects.filter(milestone__project__owner=self.request.user)

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

# Comment CRUD
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

# Attachment CRUD
class AttachmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Attachment.objects.filter(task__assignee=self.request.user)

class AttachmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
