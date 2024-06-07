import time

from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from manager.models import Manager_UserInfo
from manager.models import UserInfo
from manager.serializers import ManagerUserInfoSerializer, UserInfoSerializer
import pyrebase
import os

Config = {
  "apiKey": "AIzaSyB9d_LpVH9A9OU82xqp0Fuo-XhhjQMbksI",
  "authDomain": "ndc-annotation-tool.firebaseapp.com",
  "projectId": "ndc-annotation-tool",
  "storageBucket": "ndc-annotation-tool.appspot.com",
  "messagingSenderId": "30054694568",
  "appId": "1:30054694568:web:3a4900a7430212fcab8c9d",
  "measurementId": "G-MGCTELM2B1",
  "serviceAccount": "manager/ndc-annotation-tool-firebase-adminsdk.json",
  "databaseURL": ""
}

firebase = pyrebase.initialize_app(Config)
storage = firebase.storage()
auth = firebase.auth()
email='wangziying116@gmail.com'
password='password1004'
# Log the user in
user = auth.sign_in_with_email_and_password(email, password)
# before the 1 hour expiry:
user = auth.refresh(user['refreshToken'])
# now we have a fresh token
token=user['idToken']
# Create your views here.


class AdministratorAPIView(APIView):
    def post(self, request):
        data = JSONParser().parse(request)
        Manager_username = data.get("user")
        Manager_password = data.get("pwd")
        user_exists = Manager_UserInfo.objects.filter(Manager_username=Manager_username,
                                                      Manager_password=Manager_password).exists()
        if user_exists:
            user_url = reverse('user_functions', kwargs={'manager_username': Manager_username})
            return JsonResponse({'success': True, 'redirect_url': user_url})
        else:
            return JsonResponse({'success': False, 'error_msg': 'Login failed'})


class FunctionsAPIView(APIView):
    def get(self, request, manager_username):
        users = UserInfo.objects.using('NDC_local_db').all()
        serializer = UserInfoSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)

class AddUserInfoView(APIView):
    def get(self, request, manager_username):
        #返回用户列表
        users = UserInfo.objects.using('NDC_local_db').all()
        serializer = UserInfoSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request, manager_username):
    #添加用户信息
        data = JSONParser().parse(request)
        annotator_name = data.get("username")
        password = data.get('password')
        age = data.get('age')
        email = data.get('email')
        file_path = '.txt'  # 替换为实际的文件路径和文件名
        # 使用 'w' 模式打开文件，并创建文件（如果文件不存在）
        with open(file_path, 'w') as file:
            file.close()
        annotator_path = annotator_name + '/'
        empty_txt = storage.bucket.blob(annotator_path)
        empty_txt.upload_from_filename(file_path)
        os.remove(file_path)
        UserInfo.objects.using('NDC_local_db').create(username=annotator_name, password=password, age=age, email=email)
        #serializer = UserInfoSerializer(data=data)
        #if serializer.is_valid():
        #   serializer.save()
        #   return JsonResponse(serializer.data, status=201)

        return JsonResponse({'message': 'User add successfully'}, status=204)


# 删除用户信息
class DeleteUserInfoView(APIView):
    def delete(self,request, manager_username):
        data = JSONParser().parse(request)
        annotator_name = data.get('username')
        password = data.get('password')
        age = data.get('age')
        email = data.get('email')
        # 在这里删除对应的用户信息
        UserInfo.objects.using('NDC_local_db').filter(username=annotator_name, password=password, age=age, email=email).delete()
        dir_content = storage.bucket.list_blobs(prefix=annotator_name+'/')
        print(dir_content)
        for file in dir_content:
            storage.delete(file.name, token)
        # 返回 JSON 响应
        return JsonResponse({'message': 'User deleted successfully'}, status=204)

    def get(self, request, manager_username):
        # 如果不是 Delete 请求，返回列表
        users = UserInfo.objects.using('NDC_local_db').all()
        serializer = UserInfoSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)

# 展示用户信息
class ShowUserInfoView(APIView):
    def get(self,request, manager_username):
        # 获取所有用户信息
        data = UserInfo.objects.using('NDC_local_db').all()
        serializer = UserInfoSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)

# 更新用户信息
class UpdateUserInfoView(APIView):
    def put(self, request, manager_username):
        data = JSONParser().parse(request)
        username = data.get('old_username')
        #new_username = data.get('new_username')
        new_password = data.get('new_password')
        new_age = data.get('new_age')
        new_email = data.get('new_email')

        # 在数据库中查找要更新的用户信息
        user = UserInfo.objects.using('NDC_local_db').get(username=username)

        # 更新用户信息
        #user.username = new_username
        user.password = new_password
        user.age = new_age
        user.email = new_email
        user.save()
        '''
        dir_content = storage.bucket.list_blobs(prefix=old_username)
        filelist = [file.name for file in dir_content]
        print(filelist)
        for filename in filelist:
            destination = filename.replace(old_username, new_username)
            source_blob = storage.bucket.blob(filename)
            storage.bucket.copy_blob(source_blob, storage.bucket, destination)
            storage.delete(f'{filename}', token)
        '''
        # 返回 JSON 响应
        return JsonResponse({'message': 'User updated successfully'}, status=200)

    def get(self, request, manager_username):
        # 如果不是 Put 请求，返回列表
        users = UserInfo.objects.using('NDC_local_db').all()
        serializer = UserInfoSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)

"""
def administrator(request):
    if request.method == "GET":
        return render(request, "Manager_loginpage.html")

    Manager_username = request.POST.get("user")
    Manager_password = request.POST.get("pwd")

    user_exists = Manager_UserInfo.objects.filter(Manager_username=Manager_username,
                                                  Manager_password=Manager_password).exists()

    if user_exists:
        # 根据用户的身份信息生成个人界面的URL
        user_url = reverse('user_functions', kwargs={'username': Manager_username})
        return HttpResponseRedirect(user_url)
    else:
        return render(request, "Manager_loginpage.html", {"error_msg": "Login failed"})

def primarypage(request):
    #Manager_UserInfo.objects.create(Manager_username="admin1", Manager_password="123")
    return render(request,"primarypage.html")

def functions(request, username):
    # 处理个人界面逻辑
    return render(request, "function_page.html", {"username": username})
    
def add_functions(request, username):
    if request.method == 'POST':
        annotator_name = request.POST.get('annotator_name')
        password = request.POST.get('password')
        age = request.POST.get('age')
        email = request.POST.get('email')
        #user_type = request.POST.get('user_type')
        # 在这里将annotatorname和password保存到数据库中
        # 假设你有一个名为UserInfo的模型来存储用户信息
        file_path = '.txt'  # 替换为实际的文件路径和文件名
        # 使用 'w' 模式打开文件，并创建文件（如果文件不存在）
        with open(file_path, 'w') as file:
            file.close()
        annotator_path = annotator_name + '/'
        empty_txt = storage.bucket.blob(annotator_path)
        empty_txt.upload_from_filename(file_path)
        os.remove(file_path)
        #UserInfo.objects.using('NDC_local_db').create(username=annotator_name, password=password, age=age, email=email)

        UserInfo.objects.using('NDC_local_db').create(username=annotator_name, password=password, age=age, email=email)

        # 保存成功后，重定向到用户个人界面
        return redirect(reverse('show_functions', kwargs={'username': username}))

    return render(request, 'add_functions.html', {'username': username})
    
def del_functions(request, username):
    if request.method == 'POST':
        annotator_name = request.POST.get('annotator_name')
        password = request.POST.get('password')
        age = request.POST.get('age')
        email = request.POST.get('email')
        #user_type = request.POST.get('user_type')

        UserInfo.objects.using('NDC_local_db').delete(username=annotator_name, password=password, age=age, email=email)

        return redirect(reverse('del_functions', kwargs={'username': username}))

    return render(request, 'delete_functions.html', {'username': username})


def show_functions(request, username):
    data = UserInfo.objects.using('NDC_local_db').all()
    # 将数据传递给模板进行展示
    return render(request, "show_functions.html", {"data": data, "username": username})


def update_functions(request, username):
    if request.method == 'POST':
        # 获取表单提交的数据
        old_username = request.POST.get('old_username')
        new_username = request.POST.get('new_username')
        new_password = request.POST.get('new_password')
        new_age = request.POST.get('new_age')
        new_email = request.POST.get('new_email')

        # 在数据库中查找要更新的用户信息
        user = UserInfo.objects.using('NDC_local_db').get(username=old_username)

        # 更新用户信息
        user.username = new_username
        user.password = new_password
        user.age = new_age
        user.email = new_email
        user.save()

        return redirect(reverse('show_functions', kwargs={'username': username}))

    # 获取所有用户信息用于展示
    data = UserInfo.objects.using('NDC_local_db').all()
    return render(request, 'update_functions.html', {'data': data, 'username': username})

"""