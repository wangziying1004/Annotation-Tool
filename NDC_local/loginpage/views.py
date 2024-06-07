from django.http import HttpResponse

from loginpage.models import UserInfo
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from .serializers import UserInfoSerializer
# Create your views here.

class adminstratorAPIView(APIView):
    def get(self, request):
        response_data={
            'code':200,
            'message':'登录界面'
        }
        return JsonResponse(response_data, safe=False)
    def post(self, request):
        data = JSONParser().parse(request)
        username = data.get("user")
        password = data.get("pwd")
        user_type = data.get("user_type")
        print(data)
        user_exists = UserInfo.objects.filter(username=username, password=password).exists()
        if user_exists:
            print('user_exists')
        if user_exists and user_type == "annotator":
            # 根据用户的身份信息生成个人界面的URL
            junior_user_url = reverse('annotator_user_functions', kwargs={'username': username})
            response_data={
                'code':200,
                'message':'登录annotator页面',
                'url':junior_user_url
            }
            return JsonResponse(response_data, safe=False)
        elif user_exists and user_type == "project-owner":
            senior_user_url = reverse('project_owner_functions', kwargs={'username': username})
            response_data = {
                'code': 200,
                'message': '登录project_owner页面',
                'url': senior_user_url
            }
            return JsonResponse(response_data, safe=False)
        else:
            response_data = {
                'code': 403,
                'message': 'login failed'
            }
            return JsonResponse(response_data, safe=False)


"""
def administrator(request):
    if request.method =="GET":
      return render(request, "loginpage.html")
        #print(request.POST)
    username= request.POST.get("user")
    password= request.POST.get("pwd")
    user_type = request.POST.get("user-type")


    #if request.method == 'POST':
    #    data = request.data
    #    username = data.get('username')
    #    password = data.get('password')
    #    user_type = data.get('user_type')

    #user_exists = UserInfo.objects.filter(username=username,password=password, user_type=user_type).exists()
    user_exists = UserInfo.objects.filter(username=username,password=password).exists()

    if user_exists and user_type == "annotator":
        # 根据用户的身份信息生成个人界面的URL
        junior_user_url = reverse('annotator_user_functions', kwargs={'username': username})
        return HttpResponseRedirect(junior_user_url)
    elif user_exists and user_type == "project-owner":
        senior_user_url = reverse('project_owner_functions', kwargs={'username': username})
        return HttpResponseRedirect(senior_user_url)



    return render(request, "loginpage.html", {"error_msg": "login failed"})
"""

"""  
def primarypage(request):
    #UserInfo.objects.create(username="admin4", password="123", user_type="junior")
    #UserInfo.objects.create(username="admin1", password="456", user_type="senior")
    return render(request,"primarypage.html")
"""

class Junior_signupAPIView(APIView):
    def post(self, request):
        data = JSONParser().parse(request)
        username = data.get("user")
        password = data.get("pwd")
        user_type = data.get("user-type")

        if not (len(username) <= 32 and len(password) <= 20):
            response_data = {
                'code': 403,
                'message': 'Invalid input'
            }
            return JsonResponse(response_data, safe=False)

        # 检查用户名是否已存在
        if UserInfo.objects.filter(username=username).exists():
            response_data = {
                'code': 403,
                'message': 'Username already exists'
            }
            return JsonResponse(response_data, safe=False)

        # 创建新用户
        if user_type == "annotator":
           UserInfo.objects.create(username=username, password=password)
           junior_user_url = reverse('annotator_user_functions', kwargs={'username': username})
           response_data = {
               'code': 200,
               'message': '登录annotator页面',
               'url': junior_user_url
           }
           return JsonResponse(response_data, safe=False)

        if user_type == "project-owner":
            UserInfo.objects.create(username=username, password=password)
            senior_user_url = reverse('project_owner_functions', kwargs={'username': username})
            response_data = {
                'code': 200,
                'message': '登录project_owner页面',
                'url': senior_user_url
            }
            return JsonResponse(response_data, safe=False)
    def get(self,request):
        response_data = {
            'code': 200,
            'message': '注册界面'
        }
        return JsonResponse(response_data, safe=False)
"""
def junior_signup(request):
    if request.method == "POST":
        username = request.POST.get("user")
        password = request.POST.get("pwd")
        user_type = request.POST.get("user-type")

        # 检查输入信息是否合规
        if not (len(username) <= 32 and len(password) <= 20):
            return render(request, "signup.html", {"error_msg": "Invalid input"})

        # 检查用户名是否已存在
        if UserInfo.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error_msg": "Username already exists"})

        # 创建新用户
        if user_type == "annotator":
           UserInfo.objects.create(username=username, password=password)
           user_url = reverse('annotator_user_functions', kwargs={'username': username})
           return HttpResponseRedirect(user_url)

        if user_type == "project-owner":
            UserInfo.objects.create(username=username, password=password)
            user_url = reverse('project_owner_functions', kwargs={'username': username})
            return HttpResponseRedirect(user_url)

    return render(request, "signup.html")
"""