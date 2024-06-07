from rest_framework import serializers
from .models import Manager_UserInfo, UserInfo

class ManagerUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager_UserInfo
        fields = ['id', 'Manager_username', 'Manager_password', 'Manager_age', 'Manager_email']

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['id', 'username', 'password', 'age', 'email']
