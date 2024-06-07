from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from dataset_application.models import Dataset_Info
from manager.models import Manager_UserInfo
from rest_framework.test import APIClient


class DatasetApplicationTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.manager_user_info = Manager_UserInfo.objects.create(Manager_username='admin', Manager_password='password')
        self.dataset_info = Dataset_Info.objects.create(filename='test_folder', manager_name='admin')
        self.manager_username = 'admin'

    def test_add_dataset(self):
        data = {
            'folderName': 'new_folder'
        }
        response = self.client.post(reverse('add_dataset2', kwargs={'manager_username': self.manager_username}), data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Dataset_Info.objects.filter(filename='new_folder').exists())

    def test_delete_dataset(self):
        Dataset_Info.objects.create(filename='delete_folder', manager_name='admin')
        data = {
            'folderName': 'delete_folder'
        }
        response = self.client.delete(reverse('del_dataset', kwargs={'manager_username': self.manager_username}), data,
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Dataset_Info.objects.filter(filename='delete_folder').exists())

    def test_show_dataset(self):
        response = self.client.get(reverse('show_dataset', kwargs={'manager_username': self.manager_username}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_update_dataset(self):
        data = {
            'folderName': 'updated_folder'
        }
        response = self.client.put(reverse('update_dataset', kwargs={'manager_username': self.manager_username}), data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # You should add assertions to check the updated data if applicable

    def test_show_exact_data(self):
        folder_name = 'test_folder'
        response = self.client.get(
            reverse('show_exact_data', kwargs={'manager_username': self.manager_username, 'folder_name': folder_name}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # You should add assertions to check the exact data if applicable

    def test_delete_exact_data(self):
        folder_name = 'test_folder'
        data = {
            'file_name': 'test_file.txt'
        }
        response = self.client.delete(reverse('delete_exact_data', kwargs={'manager_username': self.manager_username,
                                                                           'folder_name': folder_name}), data,
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # You should add assertions to check if the exact data is deleted if applicable

