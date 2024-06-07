from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from django.core.management import call_command
from manager.models import UserInfo, Manager_UserInfo

class ManagerViewsTestCase(TestCase):
    databases = {'default', 'NDC_local_db'}

    @classmethod
    def setUpTestData(cls):
        call_command('migrate', database='NDC_local_db')
        cls.manager_user_info = Manager_UserInfo.objects.create(Manager_username='admin', Manager_password='password')
        cls.user_info = UserInfo.objects.using('NDC_local_db').create(username='testuser', password='password', age=30, email='testuser@example.com')

    def setUp(self):
        self.client = Client()

    def test_administrator_login(self):
        response = self.client.post(reverse('managerloginpage'), {'user': 'admin', 'pwd': 'password'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('redirect_url', response.json())

    def test_get_users(self):
        response = self.client.get(reverse('user_functions', kwargs={'manager_username': 'admin'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_add_user_info(self):
        new_user_data = {
            "username": "newuser",
            "password": "newpassword",
            "age": 25,
            "email": "newuser@example.com"
        }
        response = self.client.post(reverse('add_functions', kwargs={'manager_username': 'admin'}), new_user_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(UserInfo.objects.using('NDC_local_db').filter(username='newuser').exists())

    def test_delete_user_info(self):
        delete_user_data = {
            "username": "testuser",
            "password": "password",
            "age": 30,
            "email": "testuser@example.com"
        }
        response = self.client.delete(reverse('del_functions', kwargs={'manager_username': 'admin'}), delete_user_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserInfo.objects.using('NDC_local_db').filter(username='testuser').exists())

    def test_show_user_info(self):
        response = self.client.get(reverse('show_functions', kwargs={'manager_username': 'admin'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_update_user_info(self):
        update_user_data = {
            "old_username": "testuser",
            "new_password": "updatedpassword",
            "new_age": 35,
            "new_email": "updateduser@example.com"
        }
        response = self.client.put(reverse('update_functions', kwargs={'manager_username': 'admin'}), update_user_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = UserInfo.objects.using('NDC_local_db').get(username='testuser')
        self.assertEqual(user.password, "updatedpassword")
        self.assertEqual(user.age, 35)
        self.assertEqual(user.email, "updateduser@example.com")
