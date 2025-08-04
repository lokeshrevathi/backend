from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

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
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_manager(self):
        return self.role == 'manager'
    
    @property
    def is_user(self):
        return self.role == 'user'
    
    def can_create_users(self):
        """Check if user can create other users"""
        return self.is_admin
    
    def can_create_managers(self):
        """Check if user can create managers"""
        return self.is_admin
    
    def can_create_projects(self):
        """Check if user can create projects"""
        return True  # All authenticated users can create projects
    
    def can_assign_users(self):
        """Check if user can assign users to tasks"""
        return self.is_admin or self.is_manager
    
    def can_assign_tasks(self):
        """Check if user can assign tasks"""
        return self.is_admin or self.is_manager
    
    def can_manage_project_members(self):
        """Check if user can manage project members"""
        return self.is_admin or self.is_manager

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')

    def __str__(self):
        return self.name
    
    @property
    def members(self):
        """Get all project members including owner"""
        return User.objects.filter(
            models.Q(projectmembership__project=self) | 
            models.Q(owned_projects=self)
        ).distinct()

class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='projectmembership')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projectmembership')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('project', 'user')
        verbose_name = 'Project Member'
        verbose_name_plural = 'Project Members'
    
    def __str__(self):
        return f"{self.user.username} - {self.project.name}"
    
    def clean(self):
        """Validate constraints before saving"""
        # Constraint 1: Only users can be added to projects
        if self.user and not self.user.is_user:
            raise ValidationError({
                'user': 'Only users with "user" role can be added to projects as members.'
            })
        
        # Constraint 2: One user can be assigned to maximum 2 projects
        if self.user:
            existing_projects = ProjectMember.objects.filter(user=self.user).exclude(pk=self.pk).count()
            if existing_projects >= 2:
                raise ValidationError({
                    'user': f'User {self.user.username} is already assigned to {existing_projects} projects. Maximum allowed is 2.'
                })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Milestone(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')

    def __str__(self):
        return f"{self.title} ({self.project.name})"

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='tasks')
    logged_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.title} ({self.status})"

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.task.title}"

class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')

    def __str__(self):
        return f"{self.file.name} ({self.task.title})"
