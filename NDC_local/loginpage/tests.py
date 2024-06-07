from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from loginpage.models import UserInfo

class LoginPageTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.username = "testuser"
        self.password = "testpassword"
        self.user_type = "annotator"
        self.user = UserInfo.objects.create(username=self.username, password=self.password)

    def test_administrator_get(self):
        response = self.client.get(reverse('loginpage_views.adminstratorAPIView'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('message'), '登录界面')

    def test_administrator_post_valid_annotator(self):
        data = {
            "user": self.username,
            "pwd": self.password,
            "user_type": self.user_type
        }
        response = self.client.post(reverse('loginpage_views.adminstratorAPIView'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('message'), '登录annotator页面')

    def test_administrator_post_valid_project_owner(self):
        self.user_type = "project-owner"
        data = {
            "user": self.username,
            "pwd": self.password,
            "user_type": self.user_type
        }
        response = self.client.post(reverse('loginpage_views.adminstratorAPIView'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('message'), '登录project_owner页面')

    def test_administrator_post_invalid(self):
        data = {
            "user": "wronguser",
            "pwd": "wrongpassword",
            "user_type": self.user_type
        }
        response = self.client.post(reverse('loginpage_views.adminstratorAPIView'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('message'), 'login failed')

    def test_signup_get(self):
        response = self.client.get(reverse('junior_signup'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('message'), '注册界面')

    def test_signup_post_valid_annotator(self):
        data = {
            "user": "newannotator",
            "pwd": "newpassword",
            "user-type": "annotator"
        }
        response = self.client.post(reverse('junior_signup'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(UserInfo.objects.filter(username="newannotator").exists())
        self.assertEqual(response.json().get('message'), '登录annotator页面')

    def test_signup_post_valid_project_owner(self):
        data = {
            "user": "newprojectowner",
            "pwd": "newpassword",
            "user-type": "project-owner"
        }
        response = self.client.post(reverse('junior_signup'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(UserInfo.objects.filter(username="newprojectowner").exists())
        self.assertEqual(response.json().get('message'), '登录project_owner页面')

    def test_signup_post_invalid_input(self):
        data = {
            "user": "a" * 33,
            "pwd": "newpassword",
            "user-type": "annotator"
        }
        response = self.client.post(reverse('junior_signup'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('message'), 'Invalid input')

    def test_signup_post_existing_username(self):
        data = {
            "user": self.username,
            "pwd": "newpassword",
            "user-type": "annotator"
        }
        response = self.client.post(reverse('junior_signup'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('message'), 'Username already exists')
from django.test import TestCase

# Create your tests here.
