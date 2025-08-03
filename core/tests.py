from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, Project, Milestone, Task, Comment, Attachment
from django.core.files.uploadedfile import SimpleUploadedFile

class APITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Test@1234')
        self.other_user = User.objects.create_user(username='otheruser', password='Other@1234')
        self.client.force_authenticate(user=self.user)

    def test_registration(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'New@1234',
            'password2': 'New@1234',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        url = reverse('login')
        data = {'username': self.user.username, 'password': 'Test@1234'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_user_detail(self):
        url = reverse('user_detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    # ...existing tests for project, milestone, task, comment, attachment, log time, total hours, progress...
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Test@1234')
        self.other_user = User.objects.create_user(username='otheruser', password='Other@1234')
        self.client.force_authenticate(user=self.user)

    def test_log_time_api(self):
        project = Project.objects.create(name='Project', description='desc', start_date='2025-07-29', end_date='2025-08-29', owner=self.user)
        milestone = Milestone.objects.create(title='MS', due_date='2025-08-01', project=project)
        task = Task.objects.create(title='Task', description='desc', status='todo', priority='medium', assignee=self.user, milestone=milestone, logged_hours=1)
        url = reverse('task-log-time', args=[task.id])
        response = self.client.post(url, {'hours': 2.5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['logged_hours'], 3.5)

    def test_project_total_hours_api(self):
        project = Project.objects.create(name='Project', description='desc', start_date='2025-07-29', end_date='2025-08-29', owner=self.user)
        milestone = Milestone.objects.create(title='MS', due_date='2025-08-01', project=project)
        Task.objects.create(title='Task1', description='desc', status='todo', priority='medium', assignee=self.user, milestone=milestone, logged_hours=2)
        Task.objects.create(title='Task2', description='desc', status='done', priority='high', assignee=self.user, milestone=milestone, logged_hours=3)
        url = reverse('project-total-hours', args=[project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_hours'], 5.0)

    def test_project_progress_api(self):
        project = Project.objects.create(name='Project', description='desc', start_date='2025-07-29', end_date='2025-08-29', owner=self.user)
        milestone = Milestone.objects.create(title='MS', due_date='2025-08-01', project=project)
        Task.objects.create(title='Task1', description='desc', status='todo', priority='medium', assignee=self.user, milestone=milestone, logged_hours=2)
        Task.objects.create(title='Task2', description='desc', status='done', priority='high', assignee=self.user, milestone=milestone, logged_hours=3)
        url = reverse('project-progress', args=[project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress_percent'], 50.0)

    def test_project_permission(self):
        # User can create and access own project
        url = reverse('project-list-create')
        data = {'name': 'My Project', 'description': 'desc', 'start_date': '2025-07-29', 'end_date': '2025-08-29'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project_id = response.data['id']
        url_detail = reverse('project-detail', args=[project_id])
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Other user cannot access this project
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Switch back to owner and delete
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_task_filtering(self):
        # Create project and milestone
        project = Project.objects.create(name='Project', description='desc', start_date='2025-07-29', end_date='2025-08-29', owner=self.user)
        milestone = Milestone.objects.create(title='MS', due_date='2025-08-01', project=project)
        # Create tasks with different status and assignee
        Task.objects.create(title='Task1', description='desc', status='todo', priority='medium', assignee=self.user, milestone=milestone, logged_hours=1)
        Task.objects.create(title='Task2', description='desc', status='done', priority='high', assignee=self.other_user, milestone=milestone, logged_hours=2)
        url = reverse('task-list-create')
        # Filter by status
        response = self.client.get(url + '?status=todo')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'todo')
        # Filter by assignee
        response = self.client.get(url + f'?assignee={self.user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(task['assignee'] == self.user.id for task in response.data))

    def test_project_crud(self):
        url = reverse('project-list-create')
        data = {
            'name': 'Project Alpha',
            'description': 'First project',
            'start_date': '2025-07-29',
            'end_date': '2025-08-29',
            'owner': self.user.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project_id = response.data['id']
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url_detail = reverse('project-detail', args=[project_id])
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(url_detail, {'name': 'Project Beta'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_milestone_crud(self):
        project = Project.objects.create(name='Project', description='desc', start_date='2025-07-29', end_date='2025-08-29', owner=self.user)
        url = reverse('milestone-list-create')
        data = {'title': 'Milestone 1', 'due_date': '2025-08-01', 'project': project.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        milestone_id = response.data['id']
        url_detail = reverse('milestone-detail', args=[milestone_id])
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_crud(self):
        project = Project.objects.create(name='Project', description='desc', start_date='2025-07-29', end_date='2025-08-29', owner=self.user)
        milestone = Milestone.objects.create(title='MS', due_date='2025-08-01', project=project)
        url = reverse('task-list-create')
        data = {
            'title': 'Task 1',
            'description': 'desc',
            'status': 'todo',
            'priority': 'medium',
            'assignee': self.user.id,
            'milestone': milestone.id,
            'logged_hours': 2.5
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task_id = response.data['id']
        url_detail = reverse('task-detail', args=[task_id])
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_crud(self):
        project = Project.objects.create(name='Project', description='desc', start_date='2025-07-29', end_date='2025-08-29', owner=self.user)
        milestone = Milestone.objects.create(title='MS', due_date='2025-08-01', project=project)
        task = Task.objects.create(title='Task', description='desc', status='todo', priority='medium', assignee=self.user, milestone=milestone, logged_hours=1)
        url = reverse('comment-list-create')
        data = {'task': task.id, 'user': self.user.id, 'content': 'Nice work!'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment_id = response.data['id']
        url_detail = reverse('comment-detail', args=[comment_id])
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_attachment_crud(self):
        project = Project.objects.create(name='Project', description='desc', start_date='2025-07-29', end_date='2025-08-29', owner=self.user)
        milestone = Milestone.objects.create(title='MS', due_date='2025-08-01', project=project)
        task = Task.objects.create(title='Task', description='desc', status='todo', priority='medium', assignee=self.user, milestone=milestone, logged_hours=1)
        url = reverse('attachment-list-create')
        file = SimpleUploadedFile('test.txt', b'file_content')
        data = {'task': task.id, 'file': file}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        attachment_id = response.data['id']
        url_detail = reverse('attachment-detail', args=[attachment_id])
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
