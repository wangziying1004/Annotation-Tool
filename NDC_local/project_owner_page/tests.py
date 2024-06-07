from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from project_owner_page.models import Project_owner, TodoList
from loginpage.models import UserInfo
from juniorpage.models import detail_file_of_project, project_level


class ProjectOwnerTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = UserInfo.objects.create(username=self.username, password=self.password)
        self.project_owner = Project_owner.objects.create(project_owner_name=self.username, project_name='TestProject')

    def test_owner_function_api_view(self):
        url = reverse('project_owner_functions', args=[self.username])
        response = self.client.post(url, {'username': self.username}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.username)

    def test_pretrain_api_view_get(self):
        url = reverse('pretrain', args=[self.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('dataset_folder_list', response.data)
        self.assertIn('model_list', response.data)

    def test_pretrain_api_view_post(self):
        url = reverse('pretrain', args=[self.username])
        data = {
            'project_name': 'TestProject',
            'dataset_folder_list': 'dataset_folder',
            'model_list': 'model'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['project_name'], 'TestProject')

    def test_startproject_setlevelandtask_api_view_post(self):
        url = reverse('startproject_setlevelandtask', args=[self.username, 'TestProject'])
        data = {
            'level_number': 3,
            'max_tasks': 5,
            'folder_name': 'folder_name'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('redirect_url', response.data)

    def test_startproject_assignpeople_api_view_get(self):
        url = reverse('startproject_assignpeople', args=[self.username, 'TestProject'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('levels', response.data)
        self.assertIn('all_users', response.data)

    def test_startproject_assignpeople_api_view_post(self):
        url = reverse('startproject_assignpeople', args=[self.username, 'TestProject'])
        data = {
            'max_tasks': 5,
            'level_number': 2,
            'selected_users': {
                '1': ['user1', 'user2'],
                '2': ['user3', 'user4']
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('project_list', response.data)

    def test_show_project_api_view(self):
        url = reverse('show_project', args=[self.username, 'TestProject'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pretrained_dataset_list', response.data)

    def test_export_project_api_view(self):
        url = reverse('export_project', args=[self.username, 'TestProject'])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Disposition'], f'attachment; filename=TestProject.zip')

    def test_end_project_api_view(self):
        url = reverse('end_project', args=[self.username, 'TestProject'])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('project_list', response.data)


from django.test import TestCase

# Create your tests here.
