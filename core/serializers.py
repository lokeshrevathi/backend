
from rest_framework import serializers
from .models import User, Project, Milestone, Task, Comment, Attachment, ProjectMember
from django.contrib.auth.password_validation import validate_password

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='user', required=False)

    class Meta:
        model = User
        fields = ("username", "password", "password2", "email", "first_name", "last_name", "role")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        request = self.context.get('request')
        user_role = attrs.get('role', 'user')
        
        if request and request.user.is_authenticated:
            # Authenticated user - can create users and managers if they are admin
            if user_role in ['admin', 'manager'] and not request.user.can_create_managers():
                raise serializers.ValidationError({"role": "You don't have permission to create users with this role."})
        else:
            # Public registration - only allow 'admin' role
            if user_role != 'admin':
                raise serializers.ValidationError({"role": "Public registration only allows 'admin' role. Users and managers must be created by authenticated admins."})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ("id", "username", "password", "password2", "email", "first_name", "last_name", "role")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Only admins can create managers and admins
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_role = attrs.get('role', 'user')
            if user_role in ['admin', 'manager'] and not request.user.can_create_managers():
                raise serializers.ValidationError({"role": "You don't have permission to create users with this role."})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user

class ProjectMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    project = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = ProjectMember
        fields = ('id', 'user', 'user_id', 'project', 'joined_at')
        read_only_fields = ('joined_at',)
    
    def validate_user_id(self, value):
        """Validate that the user exists and has 'user' role"""
        try:
            user = User.objects.get(id=value)
            if not user.is_user:
                raise serializers.ValidationError("Only users with 'user' role can be added to projects.")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
    
    def validate(self, attrs):
        """Validate constraints before creating the project member"""
        user_id = attrs.get('user_id')
        project_id = self.context.get('project_id')
        
        if user_id and project_id:
            try:
                user = User.objects.get(id=user_id)
                project = Project.objects.get(id=project_id)
                
                # Check if user is already a member of this project
                if ProjectMember.objects.filter(user=user, project=project).exists():
                    raise serializers.ValidationError("User is already a member of this project.")
                
                # Check if user is at maximum limit (2 projects)
                current_project_count = ProjectMember.objects.filter(user=user).count()
                if current_project_count >= 2:
                    raise serializers.ValidationError(
                        f"User {user.username} is already assigned to {current_project_count} projects. Maximum allowed is 2."
                    )
                
                # Check if user is the project owner (shouldn't be added as member)
                if project.owner == user:
                    raise serializers.ValidationError("Project owner cannot be added as a member.")
                
            except (User.DoesNotExist, Project.DoesNotExist):
                raise serializers.ValidationError("Invalid user or project.")
        
        return attrs
    
    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)
        validated_data['user'] = user
        return super().create(validated_data)

class ProjectMemberListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    current_project_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectMember
        fields = ('id', 'user', 'joined_at', 'current_project_count')
    
    def get_current_project_count(self, obj):
        """Get the number of projects the user is currently assigned to"""
        return ProjectMember.objects.filter(user=obj.user).count()

class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    members = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = '__all__'
    
    def get_members(self, obj):
        """Get project members (excluding owner)"""
        members = ProjectMember.objects.filter(project=obj)
        return UserSerializer([member.user for member in members], many=True).data
    
    def get_member_count(self, obj):
        """Get total number of project members (including owner)"""
        return obj.members.count()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional for updates
        if self.instance is not None:  # This is an update
            for field_name in ['name', 'description', 'start_date', 'end_date']:
                if field_name in self.fields:
                    self.fields[field_name].required = False

class MilestoneSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    
    class Meta:
        model = Milestone
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional for updates
        if self.instance is not None:  # This is an update
            for field_name in ['title', 'due_date', 'project']:
                if field_name in self.fields:
                    self.fields[field_name].required = False

class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)
    milestone = serializers.PrimaryKeyRelatedField(queryset=Milestone.objects.all())
    
    class Meta:
        model = Task
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional for updates
        if self.instance is not None:  # This is an update
            for field_name in ['title', 'description', 'status', 'priority', 'assignee', 'milestone']:
                if field_name in self.fields:
                    self.fields[field_name].required = False

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    
    class Meta:
        model = Comment
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional for updates
        if self.instance is not None:  # This is an update
            for field_name in ['content', 'user', 'task']:
                if field_name in self.fields:
                    self.fields[field_name].required = False

class AttachmentSerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    
    class Meta:
        model = Attachment
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional for updates
        if self.instance is not None:  # This is an update
            for field_name in ['file', 'task']:
                if field_name in self.fields:
                    self.fields[field_name].required = False
