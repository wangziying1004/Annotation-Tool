from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from .models import Project_owner as project_owner
from .models import TodoList as todo_List
from juniorpage.models import detail_file_of_project
from juniorpage.models import ToDoList
from loginpage.models import UserInfo
from juniorpage.models import project_level
#from .models import Project as project_info
import pyrebase
import os
import math
import shutil
from pathlib import Path
from datetime import datetime
from django.utils import timezone
import zipfile
from django.http import FileResponse
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from project_owner_page.serializers import TodoListSerializer
from project_owner_page.serializers import ProjectOwnerSerializer
import subprocess

Config = {
  "apiKey": "AIzaSyB9d_LpVH9A9OU82xqp0Fuo-XhhjQMbksI",
  "authDomain": "ndc-annotation-tool.firebaseapp.com",
  "projectId": "ndc-annotation-tool",
  "storageBucket": "ndc-annotation-tool.appspot.com",
  "messagingSenderId": "30054694568",
  "appId": "1:30054694568:web:3a4900a7430212fcab8c9d",
  "measurementId": "G-MGCTELM2B1",
  "serviceAccount": "project_owner_page/ndc-annotation-tool-firebase-adminsdk.json",
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

class ownerfunctionAPIView(APIView):
    def post(self,request,username):
        data = JSONParser().parse(request)
        username = data.get('username')
        project_list = project_owner.objects.filter(project_owner_name=username)
        todo_list = todo_List.objects.filter(project_owner=username)
        # 序列化数据
        project_list_serializer = ProjectOwnerSerializer(project_list, many=True)
        todo_list_serializer = TodoListSerializer(todo_list, many=True)

        # 准备响应数据
        response_data = {
            'code':202,
            'message': '进入个人界面',
            'username':username,
            'project_list': project_list_serializer.data,
            'todo_list': todo_list_serializer.data
        }

        # 返回序列化后的数据
        return JsonResponse(response_data, safe=False)
'''
def ownerfunction(request,username):
    if request.method == 'POST':
        username = request.POST.get('username')
    project_list = project_owner.objects.filter(project_owner_name=username)
    todo_list = todo_List.objects.filter(project_owner=username)
    return render(request, "ownerfunction.html", {"username": username, "project_list": project_list, "todo_list": todo_list})
'''

class PretrainAPIView(APIView):
    def get(self,request,username):
        dataset_folder = storage.bucket.list_blobs(prefix='all_dataset_folder')
        # dataset_folder = storage.bucket.list_blobs(prefix='admin')
        dataset_folder_list = [file.name for file in dataset_folder]
        dataset_folder_list.pop(0)
        dataset_folder_list_new = []
        for folder in dataset_folder_list:
            parts = folder.split('/')
            if len(parts) >= 3:
                folder_name = parts[1]
                if folder_name not in dataset_folder_list_new:
                    dataset_folder_list_new.append(folder_name)
        # print(dataset_folder_list)
        model_folder = storage.bucket.list_blobs(prefix='all_model_folder')
        model_folder_list = [file.name for file in model_folder]
        model_folder_list.pop(0)
        model_folder_list_new = []
        for model in model_folder_list:
            parts = model.split('/')
            if len(parts) >= 3:
                model_name = parts[1]
                if model_name not in model_folder_list_new:
                    model_folder_list_new.append(model_name)

        # 准备响应数据
        response_data = {
            'code': 206,
            'message': '展示现有的数据集和模型',
            'username': username,
            "dataset_folder_list": dataset_folder_list_new,
            "model_list": model_folder_list_new
        }

        # 返回序列化后的数据
        return JsonResponse(response_data, safe=False)
    def post(self,request,username):
        data = JSONParser().parse(request)
        project_name=data.get('project_name')
        folder_name=data.get('dataset_folder_list')
        model_name=data.get('model_list')
        prefix_data = 'all_dataset_folder/' + folder_name + '/'
        # prefix_data = 'admin/test3/'
        data_folder = storage.bucket.list_blobs(prefix=prefix_data)
        data_local_path = "dataset/" + username + "/" + project_name + "/"
        if not os.path.exists(data_local_path):
            os.makedirs(data_local_path)
        for files in data_folder:
            print(files.name)
            if (files.name.endswith("obj")):
                files.download_to_filename(data_local_path + files.name.split('/')[-1])

        prefix_model = 'all_model_folder/' + model_name + '/'
        model_folder = storage.bucket.list_blobs(prefix=prefix_model)
        model_local_path = "model/" + username + "/" + project_name + "/"
        if not os.path.exists(model_local_path):
            os.makedirs(model_local_path)
        py_file_path = None
        tar_file_path = None

        for files in model_folder:
            print(files.name)
            if (files.name.endswith("tar") or files.name.endswith("py")):
                files.download_to_filename(model_local_path + files.name.split('/')[-1])
                if files.name.endswith("py"):
                    py_file_path=model_local_path + files.name.split('/')[-1]
                if files.name.endswith("tar"):
                    tar_file_path=model_local_path + files.name.split('/')[-1]
        if py_file_path:
            try:

                result = subprocess.run(['python', py_file_path, data_local_path, tar_file_path, username, model_name], capture_output=True, text=True,
                                        check=True)
                output = result.stdout
                error = result.stderr
            except subprocess.CalledProcessError as e:
                output = e.output
                error = e.stderr
            print(f"Script output: {output}")
            print(f"Script error: {error}")
        trained_dataset = 'outputs' + username + model_name +'/'
        project_owner_project_path = 'trained_dataset/' + folder_name + '/'
        for filename in os.listdir(trained_dataset):
            file_path = os.path.join(trained_dataset, filename)
            trained_data = storage.bucket.blob(project_owner_project_path)
            trained_data.upload_from_filename(file_path)
        shutil.rmtree(trained_dataset)
        # 准备响应数据
        response_data = {
            'code': 201,
            'message': '预先标注',
            'username': username,
            'project_name':project_name,
            'folder_name':folder_name
        }
        return JsonResponse(response_data, safe=False)
'''
def pretrain(request,username):
   if request.method == 'POST':
        project_name = request.POST.get('project_name')
        folder_name = request.POST.get('dataset_folder_list')
        model_name = request.POST.get('model_list')
        print(project_name, folder_name, model_name)
        prefix_data = 'all_dataset_folder/'+folder_name+'/'
        #prefix_data = 'admin/test3/'
        data_folder = storage.bucket.list_blobs(prefix=prefix_data)
        data_local_path = "dataset/"+username+"/"+project_name+"/"
        if not os.path.exists(data_local_path):
            os.makedirs(data_local_path)
        for files in data_folder:
            print(files.name)
            if(files.name.endswith("obj")):
               files.download_to_filename(data_local_path+files.name.split('/')[-1])

        prefix_model = 'all_model_folder/'+model_name+'/'
        model_folder = storage.bucket.list_blobs(prefix=prefix_model)
        model_local_path = "model/"+username+"/"+project_name+"/"
        if not os.path.exists(model_local_path):
            os.makedirs(model_local_path)
        for files in model_folder:
            print(files.name)
            if(files.name.endswith("tar") or files.name.endswith("py")):
              files.download_to_filename(model_local_path+files.name.split('/')[-1])
        return render(request,'project_setlevelandtask.html',{'username':username,'project_name':project_name,'folder_name':folder_name})
        #return redirect('startproject_setlevelandtask', username=username, project_name=project_name, folder_name=folder_name)
   else:
       dataset_folder = storage.bucket.list_blobs(prefix='all_dataset_folder')
       #dataset_folder = storage.bucket.list_blobs(prefix='admin')
       dataset_folder_list = [file.name for file in dataset_folder]
       dataset_folder_list.pop(0)
       dataset_folder_list_new=[]
       for folder in dataset_folder_list:
           parts = folder.split('/')
           if len(parts) >= 3:
               folder_name = parts[1]
               if folder_name not in dataset_folder_list_new:
                   dataset_folder_list_new.append(folder_name)
       #print(dataset_folder_list)
       model_folder = storage.bucket.list_blobs(prefix='all_model_folder')
       model_folder_list = [file.name for file in model_folder]
       model_folder_list.pop(0)
       model_folder_list_new = []
       for model in model_folder_list:
           parts = model.split('/')
           if len(parts) >= 3:
               model_name = parts[1]
               if model_name not in model_folder_list_new:
                   model_folder_list_new.append(model_name)

       return render(request, "project_pretrain.html", {"username": username, "dataset_folder_list": dataset_folder_list_new, "model_list": model_folder_list_new})
'''

class startproject_setlevelandtaskAPIView(APIView):
    def post(self, request,username,project_name):
        data = JSONParser().parse(request)
        level_number = data.get('level_number')
        max_tasks = data.get('max_tasks')
        folder_name = data.get('folder_name')
        project_owner.objects.create(project_owner_name=username, project_name=project_name, project_level=level_number,
                                     project_max_tasks=max_tasks, folder_name=folder_name)
        # project_info.objects.create(project_owner__project_owner_name=username, project_level=level_number, project_max_tasks=max_tasks)
        # 使用 QueryDict 创建包含查询参数的 URL
        query_params = QueryDict(mutable=True)
        query_params['level_number'] = level_number
        query_params['max_tasks'] = max_tasks
        file_path = '.txt'  # 替换为实际的文件路径和文件名
        # 使用 'w' 模式打开文件，并创建文件（如果文件不存在）
        with open(file_path, 'w') as file:
            file.close()
        project_owner_project_path = username + '/' + project_name + '/' + file_path
        empty_txt = storage.bucket.blob(project_owner_project_path)
        empty_txt.upload_from_filename(file_path)
        os.remove(file_path)
        # 构建重定向 URL，包含查询参数
        redirect_url = reverse('startproject_assignpeople', kwargs={'username': username, 'project_name': project_name})
        redirect_url += f"?{query_params.urlencode()}"
        response_data = {
            'redirect_url': redirect_url,
            'message': 'level和maxtask设定成功',
            'code': 200
        }
        return JsonResponse(response_data, safe=False)
    def get(self, request,username,project_name):
        response_data = {
            'code':200,
            'message':'设定level和maxtask',
            'username': username,
            'project_name': project_name
        }
        return JsonResponse(response_data, safe=False)

'''
def startproject_setlevelandtask(request,username,project_name):
    #print(folder_name)
    if request.method == 'POST':
        #project_name = request.POST.get('project_name')
        level_number = request.POST.get('level_number')
        max_tasks = request.POST.get('max_tasks')
        folder_name = request.POST.get('folder_name')
        project_owner.objects.create(project_owner_name=username, project_name=project_name,  project_level=level_number, project_max_tasks=max_tasks,folder_name=folder_name)
        #project_info.objects.create(project_owner__project_owner_name=username, project_level=level_number, project_max_tasks=max_tasks)
        # 使用 QueryDict 创建包含查询参数的 URL
        query_params = QueryDict(mutable=True)
        query_params['level_number'] = level_number
        query_params['max_tasks'] = max_tasks
        file_path = '.txt'  # 替换为实际的文件路径和文件名
        # 使用 'w' 模式打开文件，并创建文件（如果文件不存在）
        with open(file_path, 'w') as file:
            file.close()
        project_owner_project_path = username + '/' + project_name + '/' +file_path
        empty_txt = storage.bucket.blob(project_owner_project_path)
        empty_txt.upload_from_filename(file_path)
        os.remove(file_path)
        # 构建重定向 URL，包含查询参数
        redirect_url = reverse('startproject_assignpeople', kwargs={'username': username, 'project_name': project_name})
        redirect_url += f"?{query_params.urlencode()}"

        return redirect(redirect_url)
        #return redirect('startproject_assignpeople', username=username, project_name=project_name, level_number=level_number, max_tasks=max_tasks)
        #return render(request, "project_assigntask.html",{"username":username, "project_name":project_name, "level_number":level_number, "max_tasks":max_tasks})
    return render(request,"project_setlevelandtask.html",{"project_name":project_name,"username":username})

'''

class startproject_assignpeopleAPIView(APIView):
    def get(self, request, username, project_name):
        data = JSONParser().parse(request)
        max_tasks = data.get('max_tasks')
        level_number = data.get('level_number')
        levels = [f"level{i}" for i in range(1, int(level_number) + 1)]
        print(levels)
        all_users = list(UserInfo.objects.all().values())
        response_data = {
            'code': 200,
            'message': '分派任务，显示名单',
            'username': username,
            'project_name': project_name,
            "levels": levels,
            "all_users": all_users,
            "max_tasks": max_tasks
        }
        return JsonResponse(response_data, safe=False)
    def post(self, request, username, project_name):
        folder_name = project_owner.objects.get(project_owner_name=username, project_name=project_name).folder_name
        data = JSONParser().parse(request)
        max_tasks = data.get('max_tasks')
        selected_users = data.get('selected_users')
        '''
        {
        "max_tasks": 5,
        "level_number": 2,
        "selected_users": {
           "level1": ["user1", "user2"],
           "level2": ["user3", "user4"]
         }
        }
        '''
        level_number = int(data.get('level_number'))
        folder_path = os.path.join("dataset", username, project_name)
        files_count = len(os.listdir(folder_path))
        error_message = None
        for i in range(1, level_number + 1):
            level = i
            #level_name = f'level{i}'
            level_name = f"{i}"
            if not selected_users.get(level_name):
                error_message = f'No users selected for {level_name}'
                break
            # print(len(selected_users[level]))

            if (int(len(selected_users[f"{level}"])) * int(max_tasks) < int(files_count)):
                print('level', level, 'has too many tasks')
                error_message = f'Level {level} has too many tasks'
                break
        # print(max_tasks)
        # print(files_count)
        if error_message:
            all_users = list(UserInfo.objects.all().values())
            levels = [f"level{i}" for i in range(1, level_number + 1)]
            # Reload the page with the error message displayed
            response_data = {
                'code': 403,
                'message': error_message,
                'username': username,
                'project_name': project_name,
                "levels": levels,
                "all_users": all_users,
                "max_tasks": max_tasks
            }
            return JsonResponse(response_data, safe=False)

        # 保存选定的用户名到数据库
        #print(selected_users[1])
        for level, users in selected_users.items():
            for user in users:
                project_level.objects.create(annotator_name=user, project_name=project_name, level_set=int(level),
                                             project_start_date=timezone.now(), folder_name=folder_name)

        files = os.listdir(folder_path)
        files_per_person = math.floor(files_count / len(selected_users['1']))
        remaining_files = files_count % len(selected_users['1'])

        for people in selected_users['1']:
            assigned_files = files_per_person
            if remaining_files > 0:
                assigned_files += 1
                remaining_files -= 1
            # people_folder_path = people+"/"
            # people_folder = storage.bucket.blob(people_folder_path)
            # print(people_folder_path)
            person_files = files[:assigned_files]
            for person_file in person_files:
                """
                person_file=person_file.split('.')[0]
                local_file_path = folder_path+"/"+person_file+".obj"
                print(local_file_path)
                firebase_folder_path = people+"/"+project_name+"/"+person_file+".obj"
                people_folder = storage.bucket.blob(firebase_folder_path)
                people_folder.upload_from_filename(local_file_path)
                people_folder.make_public()
                """
                person_file = person_file.split('.')[0]
                detail_file_of_project.objects.create(annotator_name=people, project_name=project_name, level_set=1,
                                                      filename=person_file.split('/')[-1], people_sent=username)
            files = files[assigned_files:]

        project_list = list(project_owner.objects.filter(project_owner_name=username).values())
        todo_list = list(todo_List.objects.filter(project_owner=username).values())
        shutil.rmtree('dataset/' + username + '/' + project_name + '/')
        shutil.rmtree('model/' + username + '/' + project_name + '/')
        response_data = {
            'code': 201,
            'message': '成功分派任务',
            'username': username,
            "project_list": project_list,
            "todo_list": todo_list
        }
        return JsonResponse(response_data, safe=False)


'''
def startproject_assignpeople(request,username,project_name):
    #level_number = request.POST.get('level_number')
    if request.method == 'GET':
        max_tasks = request.GET.get('max_tasks')
        level_number = request.GET.get('level_number')
        levels = [f"level{i}" for i in range(1, int(level_number) + 1)]
        print(levels)
        all_users = UserInfo.objects.all()
        return render(request, "project_assigntask.html",
                      {"username": username, "project_name": project_name, "levels": levels, "all_users": all_users, "max_tasks": max_tasks})
    elif request.method == 'POST':
        folder_name = project_owner.objects.get(project_owner_name=username, project_name=project_name).folder_name
        max_tasks = request.POST.get('max_tasks')
        selected_users = {}
        level_number = int(request.POST.get('level_number'))
        folder_path = os.path.join("dataset", username, project_name)
        files_count = len(os.listdir(folder_path))
        error_message = None
        for i in range(1, level_number + 1):
            level = i
            level_name = f'level{i}'
            selected_users[level] = request.POST.getlist(f'{level_name}_users')
            #print(len(selected_users[level]))

            if( int(len(selected_users[level])) * int(max_tasks) < int(files_count) ):
                print('level',level,'has too many tasks')
                error_message = f'Level {level} has too many tasks'
                break
        #print(max_tasks)
        #print(files_count)
        if error_message:
            all_users = UserInfo.objects.all()
            levels =[f"level{i}" for i in range(1, level_number + 1)]
            # Reload the page with the error message displayed
            context = {"username": username, "project_name": project_name, "levels": levels, "all_users": all_users,
                       "max_tasks": max_tasks, "error_message": error_message}
            return render(request, "project_assigntask.html", context)

        # 保存选定的用户名到数据库
        print(selected_users[1])
        for level, users in selected_users.items():
            for user in users:
                project_level.objects.create(annotator_name=user, project_name=project_name, level_set=level, project_start_date=timezone.now(),folder_name=folder_name)

        files = os.listdir(folder_path)
        files_per_person = math.floor(files_count / len(selected_users[1]))
        remaining_files = files_count % len(selected_users[1])
        
        for people in selected_users[1]:
            assigned_files = files_per_person
            if remaining_files > 0:
                assigned_files += 1
                remaining_files -= 1
            #people_folder_path = people+"/"
            #people_folder = storage.bucket.blob(people_folder_path)
            #print(people_folder_path)
            person_files = files[:assigned_files]
            for person_file in person_files:
                """
                person_file=person_file.split('.')[0]
                local_file_path = folder_path+"/"+person_file+".obj"
                print(local_file_path)
                firebase_folder_path = people+"/"+project_name+"/"+person_file+".obj"
                people_folder = storage.bucket.blob(firebase_folder_path)
                people_folder.upload_from_filename(local_file_path)
                people_folder.make_public()
                """
                person_file=person_file.split('.')[0]
                detail_file_of_project.objects.create(annotator_name=people, project_name=project_name, level_set=1, filename=person_file.split('/')[-1],people_sent=username)
            files = files[assigned_files:]

        project_list = project_owner.objects.filter(project_owner_name=username)
        todo_list = todo_List.objects.filter(project_owner=username)
        shutil.rmtree('dataset/'+ username+ '/'+ project_name+'/')
        shutil.rmtree('model/'+ username+ '/'+ project_name+'/')
        return render(request, "ownerfunction.html", {"username": username, "project_list": project_list, "todo_list": todo_list})
'''

class show_projectAPIView(APIView):
    def get(self, request,username,project_name):
        dataset_received_folder = storage.bucket.list_blobs(prefix=username + "/" + project_name + "/")

        dataset_received_list = [file.name for file in dataset_received_folder]
        dataset_received_list.pop(0)
        dataset_received_list_new = []
        for data in dataset_received_list:
            parts = data.split('/')
            if len(parts) >= 3:
                data_name = parts[2]
                if data_name not in dataset_received_list_new:
                    dataset_received_list_new.append(data_name)
        #####
        folder_name = project_owner.objects.get(project_owner_name=username, project_name=project_name).folder_name
        pretrained_dataset = storage.bucket.list_blobs(prefix="trained_dataset/" + folder_name + "/")
        #pretrained_dataset = storage.bucket.list_blobs(prefix="all_dataset_folder/" + folder_name + "/")
        pretrained_dataset_list = [file.name.split('/')[-1] for file in pretrained_dataset]
        pretrained_dataset_list.pop(0)
        response_data={
            'code': 200,
            'message': '显示现有的project细节',
            "username": username,
            "project_name": project_name,
            "pretrained_dataset_list":pretrained_dataset_list,
            "dataset_received_list_new":dataset_received_list_new
        }
        return JsonResponse(response_data, safe=False)

'''
def show_project(request,username,project_name):
    if request.method == "GET":
        #todo_list = project_owner.objects.filter(project_owner_name=username,todolist__todo_list_name=project_name)
        dataset_received_folder = storage.bucket.list_blobs(prefix=username+"/"+project_name+"/")

        dataset_received_list = [file.name for file in dataset_received_folder]
        print(dataset_received_list)
        dataset_received_list.pop(0)
        dataset_received_list_new = []
        for data in dataset_received_list:
            parts = data.split('/')
            if len(parts) >= 3:
                data_name = parts[2]
                if data_name not in dataset_received_list_new:
                    dataset_received_list_new.append(data_name)
        print(dataset_received_list_new)
        #####

        folder_name = project_owner.objects.get(project_owner_name=username, project_name=project_name).folder_name
        pretrained_dataset = storage.bucket.list_blobs(prefix="all_dataset_folder/"+folder_name+"/")
        pretrained_dataset_list = [file.name.split('/')[-1] for file in pretrained_dataset]
        pretrained_dataset_list.pop(0)
        print(pretrained_dataset_list)


        return render(request,"show_project.html",{"username": username, "project_name": project_name, "pretrained_dataset_list":pretrained_dataset_list,"dataset_received_list_new":dataset_received_list_new})
'''

class export_projectAPIView(APIView):
    def post(self, request,username,project_name):
        dataset_folder = project_owner.objects.get(project_owner_name=username, project_name=project_name).folder_name
        data_tmp_folder = 'data_tmp_folder/' + username + '/' + project_name + '/'
        real_data_tmp_folder = 'real_data_tmp_folder/' + username + '/' + project_name + '/'
        merge_data_tmp_folder = 'merge_data_tmp_folder/' + username + '/' + project_name + '/'
        zip_folder = 'zip_folder/' + username + '/' + project_name + '/'
        if not os.path.exists(real_data_tmp_folder):
            os.makedirs(real_data_tmp_folder)
        if not os.path.exists(data_tmp_folder):
            os.makedirs(data_tmp_folder)
        if not os.path.exists(merge_data_tmp_folder):
            os.makedirs(merge_data_tmp_folder)
        if not os.path.exists(zip_folder):
            os.makedirs(zip_folder)

        export_folder = storage.bucket.list_blobs(prefix=username + "/" + project_name + "/")
        # export_folder.pop(0)
        original_folder = storage.bucket.list_blobs(prefix='all_dataset_folder/' + dataset_folder + "/")
        export_files_set = set()
        for files in export_folder:

            if (files.name.endswith(".txt")) and (files.name.split('/')[-1] != ".txt"):
                print(files.name)
                export_files_set.add(files.name.split('/')[-1].split('.')[0])
                files.download_to_filename(data_tmp_folder + files.name.split('/')[-1])
        for files in original_folder:
            # print(files.name)
            # if (files.name.endswith(".obj")):
            if files.name.split('/')[-1].split('.')[0] in export_files_set and files.name.endswith(".obj"):
                print(files.name)
                files.download_to_filename(real_data_tmp_folder + files.name.split('/')[-1])
        color_mapping = {
            0: '[0.3922, 0.3922, 0.3922]',
            1: '[0.0275, 0.1176, 0.1333]',
            2: '[0.9686, 0.5294, 0.3922]',
            3: '[0.3882, 0.2549, 0.2000]',
            4: '[0.1373, 0.1098, 0.0275]',
            5: '[0.8118, 0.9490, 0.4941]',
            6: '[0.8980, 0.6980, 0.3647]',
            7: '[0.6941, 0.9725, 0.9490]',
            8: '[0.9765, 0.9294, 0.8000]',
            9: '[0.9765, 0.8745, 0.4549]',
            10: '[0.5765, 0.5059, 1.0000]',
            11: '[0.9294, 0.6824, 0.2863]',
            12: '[0.3804, 0.1294, 0.0588]',
            13: '[0.1137, 0.4706, 0.4549]',
            14: '[0.4039, 0.5725, 0.5373]',
            15: '[0.9569, 0.7529, 0.5843]',
            16: '[0.9333, 0.1804, 0.1922]'
        }
        for file_name in os.listdir(data_tmp_folder):
            if file_name.endswith('.txt'):
                base_name = os.path.splitext(file_name)[0]
                obj_file_path = os.path.join(real_data_tmp_folder, base_name + '.obj')
                txt_file_path = os.path.join(data_tmp_folder, base_name + '.txt')
                result_file_path = os.path.join(merge_data_tmp_folder, base_name + '.obj')

                with open(obj_file_path, 'r') as obj_file:
                    obj_lines = obj_file.readlines()
                with open(txt_file_path, 'r') as txt_file:
                    txt_lines = txt_file.readlines()

                with open(result_file_path, 'w') as result_file:
                    i = 0
                    for line in obj_lines:
                        if line.startswith('v'):
                            idx = int(txt_lines[i].split()[1])
                            i += 1
                            color_info = color_mapping.get(idx, '[0.0, 0.0, 0.0]')
                            color_info = ', '.join(color_info.strip('[]').split(', '))
                            new_line = f'{line.split()[0]} {line.split()[1]} {line.split()[2]} {line.split()[3]} {color_info}\n'
                            result_file.write(new_line)

        zip_file_path = os.path.join(zip_folder + project_name + '.zip')

        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, _, files in os.walk(merge_data_tmp_folder):
                for file in files:
                    if file.endswith('.obj'):
                        zipf.write(os.path.join(root, file), arcname=file)
        shutil.rmtree(data_tmp_folder + "/")
        shutil.rmtree(real_data_tmp_folder + "/")
        shutil.rmtree(merge_data_tmp_folder + "/")
        return FileResponse(open(zip_file_path, 'rb'), as_attachment=True, filename=project_name + '.zip')

"""
def export_project(request,username,project_name):
    if request.method == "POST":
        #username = request.POST["username"]
        #project_name = request.POST["project_name"]
        dataset_folder= project_owner.objects.get(project_owner_name=username, project_name=project_name).folder_name
        data_tmp_folder = 'data_tmp_folder/' + username + '/' + project_name + '/'
        real_data_tmp_folder = 'real_data_tmp_folder/' + username + '/' + project_name + '/'
        merge_data_tmp_folder = 'merge_data_tmp_folder/' + username + '/' + project_name + '/'
        zip_folder = 'zip_folder/' + username + '/'+ project_name + '/'
        if not os.path.exists(real_data_tmp_folder):
            os.makedirs(real_data_tmp_folder)
        if not os.path.exists(data_tmp_folder):
            os.makedirs(data_tmp_folder)
        if not os.path.exists(merge_data_tmp_folder):
            os.makedirs(merge_data_tmp_folder)

        export_folder = storage.bucket.list_blobs(prefix=username + "/" + project_name + "/")
        #export_folder.pop(0)
        original_folder = storage.bucket.list_blobs(prefix='all_dataset_folder/' + dataset_folder + "/")
        export_files_set = set()
        for files in export_folder:

            if (files.name.endswith(".txt")) and (files.name.split('/')[-1] != ".txt"):
                print(files.name)
                export_files_set.add(files.name.split('/')[-1].split('.')[0])
                files.download_to_filename(data_tmp_folder + files.name.split('/')[-1])
        for files in original_folder:
            #print(files.name)
            #if (files.name.endswith(".obj")):
            if files.name.split('/')[-1].split('.')[0] in export_files_set and files.name.endswith(".obj"):
                print(files.name)
                files.download_to_filename(real_data_tmp_folder + files.name.split('/')[-1])
        #将label和obj合并
        '''
        download_folder = Path.home() / 'Downloads'
        print(download_folder)
        data_local_path = os.path.join(download_folder, project_name)
        os.makedirs(data_local_path, exist_ok=True)
        print(data_local_path)
        '''
        color_mapping = {
            0: '[0.3922, 0.3922, 0.3922]',
            1: '[0.0275, 0.1176, 0.1333]',
            2: '[0.9686, 0.5294, 0.3922]',
            3: '[0.3882, 0.2549, 0.2000]',
            4: '[0.1373, 0.1098, 0.0275]',
            5: '[0.8118, 0.9490, 0.4941]',
            6: '[0.8980, 0.6980, 0.3647]',
            7: '[0.6941, 0.9725, 0.9490]',
            8: '[0.9765, 0.9294, 0.8000]',
            9: '[0.9765, 0.8745, 0.4549]',
            10: '[0.5765, 0.5059, 1.0000]',
            11: '[0.9294, 0.6824, 0.2863]',
            12: '[0.3804, 0.1294, 0.0588]',
            13: '[0.1137, 0.4706, 0.4549]',
            14: '[0.4039, 0.5725, 0.5373]',
            15: '[0.9569, 0.7529, 0.5843]',
            16: '[0.9333, 0.1804, 0.1922]'
        }
        for file_name in os.listdir(data_tmp_folder):
            if file_name.endswith('.txt'):
                base_name = os.path.splitext(file_name)[0]
                obj_file_path = os.path.join(real_data_tmp_folder, base_name + '.obj')
                txt_file_path = os.path.join(data_tmp_folder, base_name + '.txt')
                result_file_path = os.path.join(merge_data_tmp_folder, base_name + '.obj')

                with open(obj_file_path, 'r') as obj_file:
                    obj_lines = obj_file.readlines()
                with open(txt_file_path, 'r') as txt_file:
                    txt_lines = txt_file.readlines()

                with open(result_file_path, 'w') as result_file:
                    i = 0
                    for line in obj_lines:
                        if line.startswith('v'):
                            idx = int(txt_lines[i].split()[1])
                            i += 1
                            color_info = color_mapping.get(idx, '[0.0, 0.0, 0.0]')
                            color_info = ', '.join(color_info.strip('[]').split(', '))
                            new_line = f'{line.split()[0]} {line.split()[1]} {line.split()[2]} {line.split()[3]} {color_info}\n'
                            result_file.write(new_line)

        zip_file_path = os.path.join(zip_folder + project_name + '.zip')
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, _, files in os.walk(merge_data_tmp_folder):
                for file in files:
                    if file.endswith('.obj'):
                        zipf.write(os.path.join(root, file), arcname=file)
        shutil.rmtree(data_tmp_folder + "/")
        shutil.rmtree(real_data_tmp_folder + "/")
        shutil.rmtree(merge_data_tmp_folder + "/")
        return redirect('show_project', username=username, project_name=project_name)
"""

class end_projectAPIView(APIView):
    def post(self, request,username,project_name):
        zip_folder = 'zip_folder/' + username + '/' + project_name + '/'
        shutil.rmtree(zip_folder + "/")
        folder_name = project_owner.objects.get(project_owner_name=username, project_name=project_name).folder_name
        trained_dataset_path = 'trained_dataset/' + folder_name + '/'
        project = project_owner.objects.filter(project_owner_name=username, project_name=project_name)
        # 如果找到了对应的项目，则执行删除操作
        if project:
            project.delete()
            # 删除成功后重定向到指定页面
        project_annotator = detail_file_of_project.objects.filter(project_name=project_name)
        if project_annotator:
            project_annotator.delete()
        project = project_level.objects.filter(project_name=project_name)
        if project:
            project.delete()
        project = todo_List.objects.filter(project_name=project_name)
        if project:
            project.delete()
        project = ToDoList.objects.filter(project_name=project_name)
        if project:
            project.delete()
        project_list = project_owner.objects.filter(project_owner_name=username)
        todo_list = todo_List.objects.filter(project_owner=username)
        project_list_serializer = ProjectOwnerSerializer(project_list, many=True)
        todo_list_serializer = TodoListSerializer(todo_list, many=True)
        firebase_trained_data = storage.bucket.list_blobs(prefix=trained_dataset_path)
        for file in firebase_trained_data:
            storage.delete(file.name, token)

        response_data = {
            'code': 200,
            'message': '删除项目',
            "username": username,
            "project_list": project_list_serializer,
            "todo_list": todo_list_serializer
        }
        return JsonResponse(response_data, safe=False)

'''
def end_project(request,username, project_name):
    zip_folder = 'zip_folder/' + username + '/' + project_name + '/'
    shutil.rmtree( zip_folder + "/")
    project = project_owner.objects.filter(project_owner_name=username, project_name=project_name)
    # 如果找到了对应的项目，则执行删除操作
    if project:
        project.delete()
        # 删除成功后重定向到指定页面
    project_annotator = detail_file_of_project.objects.filter(project_name=project_name)
    if project_annotator:
        project_annotator.delete()
    project=project_level.objects.filter(project_name=project_name)
    if project:
        project.delete()
    project = todo_List.objects.filter(project_name=project_name)
    if project:
        project.delete()
    project = ToDoList.objects.filter(project_name=project_name)
    if project:
        project.delete()
    project_list = project_owner.objects.filter(project_owner_name=username)
    todo_list = todo_List.objects.filter(project_owner=username)
    return render(request, "ownerfunction.html", {"username": username, "project_list": project_list, "todo_list": todo_list})
'''

