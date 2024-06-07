from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from loginpage.models import UserInfo
from juniorpage.models import project_level, detail_file_of_project, ToDoList
from project_owner_page.models import Project_owner

class JuniorPageTests(APITestCase):

    def setUp(self):
        self.username = 'annotator'
        self.project_name = 'test_project'
        self.user = UserInfo.objects.create(username=self.username, password='password123')
        self.project_owner = Project_owner.objects.create(project_name=self.project_name, project_owner_name='owner')
        self.project_detail = project_level.objects.create(annotator_name=self.username, project_name=self.project_name, level_set=1)
        self.detail_file = detail_file_of_project.objects.create(annotator_name=self.username, project_name=self.project_name, level_set=1, filename='test_file.obj', people_sent='owner')

    def test_junior_function(self):
        url = reverse('annotator_user_functions', kwargs={'username': self.username})
        data = {
            'username': self.username
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '进入annotator界面')

    def test_show_project(self):
        url = reverse('show_project_functions', kwargs={'username': self.username, 'project_name': self.project_name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '显示project')

    def test_annotate_project(self):
        url = reverse('annotate_project', kwargs={'username': self.username, 'project_name': self.project_name})
        data = {
            'file_name': 'test_file.obj'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_return_file(self):
        url = reverse('return_file', kwargs={'username': self.username, 'project_name': self.project_name})
        data = {
            'file_name': 'test_file.obj',
            'description': 'Test return description'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], '返回任务')
from django.test import TestCase

# Create your tests here.
