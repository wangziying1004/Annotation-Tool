import os

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import FileResponse
from .models import File
from .models import project_level as project_detail
from project_owner_page.models import Project_owner
from .models import detail_file_of_project
from .models import ToDoList
from django.templatetags.static import static
from project_owner_page.models import TodoList as project_owner_todolist
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
import json
import pyrebase
import math
import shutil
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from .serializers import ProjectLevelSerializer
from .serializers import ToDoListSerializer
from .serializers import detail_file_of_projectSerializer

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

class juniorfunctionAPIView(APIView):
    def post(self, request,username):
        data = JSONParser().parse(request)
        username=data.get('username')
        project_list = project_detail.objects.filter(annotator_name=username)
        project_list_serializer = detail_file_of_projectSerializer(project_list, many=True)
        response_data={
            'code':200,
            'message':'进入annotator界面',
            'username':username,
            'project_list':project_list_serializer.data
        }
        return JsonResponse(response_data, safe=False)

"""
def juniorfunction(request,username):
    if request.method =='POST':
        username = request.POST.get('username')
    project_list = project_detail.objects.filter(annotator_name=username)

    return render(request, "juniorpage.html", {"username": username, "project_list": project_list})
"""

class show_projectAPIView(APIView):
    def get(self, request, username,project_name):
        project_data_list = list(detail_file_of_project.objects.filter(annotator_name=username,
                                                                  project_name=project_name).values_list('filename',
                                                                                                         flat=True))
        todo_list = list(ToDoList.objects.filter(annotator_name=username,
                                            project_name=project_name).values_list('file_name',
                                                                                   flat=True))
        tmp_level = project_detail.objects.get(annotator_name=username, project_name=project_name).level_set
        data_tmp_folder = 'data_tmp_folder/' + username + '/' + project_name + '/' + "level" + str(tmp_level) + '/'
        if not os.path.exists(data_tmp_folder):
            os.makedirs(data_tmp_folder)
        # real_data_tmp_folder用来存放obj文件，data_tmp_folder用来存放label文件
        real_data_tmp_folder = 'real_data_tmp_folder/' + username + '/' + project_name + '/' + "level" + str(
            tmp_level) + '/'
        if not os.path.exists(real_data_tmp_folder):
            os.makedirs(real_data_tmp_folder)
        response_data = {
            'code': 200,
            'message': '显示project',
            'username': username,
            "project_data_list":project_data_list,
            "todo_list":todo_list
        }
        return JsonResponse(response_data, safe=False)
    def post(self, request, username,project_name):
        project_owner_name = Project_owner.objects.get(project_name=project_name).project_owner_name

        total_project_level = Project_owner.objects.get(project_name=project_name).project_level
        print(total_project_level)
        max_project_task = Project_owner.objects.get(project_name=project_name).project_max_tasks
        print(max_project_task)
        tmp_level = project_detail.objects.get(annotator_name=username, project_name=project_name).level_set
        data_tmp_folder = 'data_tmp_folder/' + username + '/' + project_name + '/' + "level" + str(tmp_level) + '/'
        real_data_tmp_folder = 'real_data_tmp_folder/' + username + '/' + project_name + '/' + "level" + str(
            tmp_level) + '/'
        merge_data_tmp_folder = 'merge_data_tmp_folder/' + username + '/' + project_name + '/' + "level" + str(
            tmp_level) + '/'
        if not os.path.exists(data_tmp_folder):
            os.makedirs(data_tmp_folder)
        #real_data_tmp_files = os.listdir(real_data_tmp_folder)
        merge_data_tmp_files = os.listdir(merge_data_tmp_folder)
        # annotator_label_list = storage.bucket.list_blobs(prefix=username + '/' + project_name + '/')
        #print(real_data_tmp_files)
        tmp_list = [file.split('/')[-1] for file in merge_data_tmp_files]
        if tmp_level == total_project_level:

            for file in tmp_list:
                #将所有文件传给project_owner
                prefix_label = username + '/' + project_name + '/' + file.split('.')[0]+'.txt'
                destination = project_owner_name + '/' + project_name + '/' + file.split('.')[0]+'.txt'
                source_blob = storage.bucket.blob(prefix_label)
                storage.bucket.copy_blob(source_blob, storage.bucket, destination)
                #传输之后删除
                storage.delete(prefix_label, token)
                person_file_name = file.split('.')[0]
                if detail_file_of_project.objects.filter(annotator_name=username, project_name=project_name,
                                                         level_set=tmp_level - 1,
                                                         filename=person_file_name.split('/')[-1]).exists():
                    detail_file_of_project.objects.get(annotator_name=username, project_name=project_name,
                                                       level_set=tmp_level - 1,
                                                       filename=person_file_name.split('/')[-1]).delete()
                if ToDoList.objects.filter(project_name=project_name, annotator_name=username,
                                           file_name=person_file_name.split('/')[-1]).exists():
                    ToDoList.objects.get(project_name=project_name, annotator_name=username,
                                         file_name=person_file_name.split('/')[-1]).delete()
            shutil.rmtree(data_tmp_folder + "/")
            shutil.rmtree(real_data_tmp_folder + "/")
            shutil.rmtree(merge_data_tmp_folder + "/")
            project_data_list = list(detail_file_of_project.objects.filter(annotator_name=username,
                                                                      project_name=project_name).values_list('filename',
                                                                                                             flat=True))
            todo_list = list(ToDoList.objects.filter(annotator_name=username,
                                                project_name=project_name).values_list('file_name',
                                                                                       flat=True))
            response_data={
                'code':201,
                'message':'向下一级分配任务',
                'username': username,
                'project_name': project_name,
                'project_data_list': project_data_list,
                'todo_list':todo_list
            }
            return JsonResponse(response_data, safe=False)
        else:
            tmp_level+=1
            higher_level_annotator_name = project_detail.objects.filter(project_name=project_name,level_set=tmp_level).values_list('annotator_name',flat=True)
            print(higher_level_annotator_name)
            #files = os.listdir(data_tmp_folder)
            #files_count = len(files)
            files_count = len(tmp_list)
            files_per_person = math.floor(files_count / len(higher_level_annotator_name))
            remaining_files = files_count % len(higher_level_annotator_name)
            print('files_per_person', files_per_person)
            print('remaining_files', remaining_files)
            min_files_person = None
            min_files_count = float('inf')
            # 对于当前任务级别，找到拥有最少任务的人员

            for person in higher_level_annotator_name:
                records = detail_file_of_project.objects.filter(annotator_name=person,project_name=project_name,level_set=tmp_level).exists()
                if records == True:
                    person_files_count = len(detail_file_of_project.objects.filter(annotator_name=person,project_name=project_name,level_set=tmp_level))
                else:
                    person_files_count =0
                print('person',person)
                print('person_files_count', person_files_count)
                if person_files_count <= min_files_count:
                    min_files_count = person_files_count
                    min_files_person = person
                # 最后将 lowest_file_count_person 设为负责人
                people = min_files_person
                assigned_files = files_per_person
                if remaining_files > 0:
                    assigned_files += 1
                    remaining_files -= 1
            # 分派任务给负责人
                person_files = tmp_list[:assigned_files]
                print('people',people)
                print('这个人分配多少任务', len(person_files))
                for person_file in person_files:
                    prefix_label = username + '/' + project_name + '/' + person_file.split('.')[0]+'.txt'
                    destination = people + '/' + project_name + '/' + person_file.split('.')[0]+'.txt'
                    source_blob = storage.bucket.blob(prefix_label)
                    storage.bucket.copy_blob(source_blob, storage.bucket, destination)
                    # 传输之后删除
                    storage.delete(prefix_label, token)
                    person_file_name = person_file.split('.')[0]
                # 创建新的记录，标记负责人和任务
                    detail_file_of_project.objects.create(annotator_name=people, project_name=project_name,
                                                      level_set=tmp_level,
                                                      filename=person_file_name.split('/')[-1], people_sent=username)
                # 删除之前的记录
                    if detail_file_of_project.objects.filter(annotator_name=username, project_name=project_name,level_set=tmp_level - 1,filename=person_file_name.split('/')[-1]).exists():
                       detail_file_of_project.objects.get(annotator_name=username, project_name=project_name,
                                                   level_set=tmp_level - 1,
                                                   filename=person_file_name.split('/')[-1]).delete()
                    if ToDoList.objects.filter(project_name=project_name,annotator_name=username,file_name=person_file_name.split('/')[-1]).exists():
                        ToDoList.objects.get(project_name=project_name, annotator_name=username,
                                                              file_name=person_file_name.split('/')[-1]).delete()
                tmp_list = tmp_list[assigned_files:]
            shutil.rmtree(data_tmp_folder + "/")
            shutil.rmtree(real_data_tmp_folder + "/")
            shutil.rmtree(merge_data_tmp_folder + "/")
            project_data_list = detail_file_of_project.objects.filter(annotator_name=username,
                                                                      project_name=project_name).values_list('filename',
                                                                                                             flat=True)
            todo_list = ToDoList.objects.filter(annotator_name=username,
                                                project_name=project_name).values_list('file_name',
                                                                                       flat=True)
            response_data = {
                'code': 201,
                'message': '向下一级分配任务',
                'username': username,
                'project_name': project_name,
                'project_data_list': project_data_list,
                'todo_list': todo_list
            }
            return JsonResponse(response_data, safe=False)
"""
def show_project(request,username,project_name):
    if request.method =='GET':
        # 显示列表
        '''
        prefix_data=username + '/' + project_name + '/'
        project_data_folder = storage.bucket.list_blobs(prefix=prefix_data)
        project_data_list = [file.name.split('/')[-1] for file in project_data_folder]
        project_data_list.pop(0)
        '''
        project_data_list = detail_file_of_project.objects.filter(annotator_name=username,
                                                                  project_name=project_name).values_list('filename',
                                                                                                         flat=True)
        todo_list = ToDoList.objects.filter(annotator_name=username,
                                                                  project_name=project_name).values_list('file_name',
                                                                                                         flat=True)
        tmp_level = project_detail.objects.get(annotator_name=username, project_name=project_name).level_set
        data_tmp_folder = 'data_tmp_folder/' + username + '/' + project_name + '/' + "level" + str(tmp_level) + '/'
        if not os.path.exists(data_tmp_folder):
            os.makedirs(data_tmp_folder)
        # real_data_tmp_folder用来存放obj文件，data_tmp_folder用来存放label文件
        real_data_tmp_folder = 'real_data_tmp_folder/' + username + '/' + project_name + '/' + "level" + str(
            tmp_level) + '/'
        if not os.path.exists(real_data_tmp_folder):
            os.makedirs(real_data_tmp_folder)
        #tmp_level = project_detail.objects.filter(annotator_name=username, project_name=project_name).level_set
        #data_tmp_folder = 'data_tmp_folder/' + username + '/' + project_name + '/' + tmp_level + '/'
        #if not os.path.exists(data_tmp_folder):
        #    os.makedirs(data_tmp_folder)
        #for file in project_data_list:
        #    file.download_to_filename(data_tmp_folder + file.name.split('/')[-1])
        return render(request, "annotator_show_project.html", {"username":username, "project_name":project_name, "project_data_list":project_data_list, "todo_list":todo_list})
    elif request.method =='POST':
        # post：confirm
        project_owner_name = Project_owner.objects.get(project_name=project_name).project_owner_name

        total_project_level = Project_owner.objects.get(project_name=project_name).project_level
        print(total_project_level)
        max_project_task = Project_owner.objects.get(project_name=project_name).project_max_tasks
        print(max_project_task)
        tmp_level = project_detail.objects.get(annotator_name=username, project_name=project_name).level_set
        data_tmp_folder = 'data_tmp_folder/' + username + '/' + project_name + '/' + "level"+str(tmp_level) + '/'
        real_data_tmp_folder = 'real_data_tmp_folder/' + username + '/' + project_name + '/' + "level" + str(tmp_level) + '/'
        merge_data_tmp_folder = 'merge_data_tmp_folder/' + username + '/' + project_name + '/' + "level" + str(tmp_level) + '/'
        if not os.path.exists(data_tmp_folder):
            os.makedirs(data_tmp_folder)
        real_data_tmp_files = os.listdir(real_data_tmp_folder)
        #annotator_label_list = storage.bucket.list_blobs(prefix=username + '/' + project_name + '/')
        print(real_data_tmp_files)
        tmp_list=[file.split('/')[-1] for file in real_data_tmp_files ]
        #tmp_list = [file.split('/')[-1] for file in merge_data_tmp_files]
        #for file in annotator_label_list:
        #    if (file.name.endswith(".txt")):
        #        tmp_list.append(file.name.split('/')[-1])
        #        #files.download_to_filename(data_tmp_folder + files.name.split('/')[-1])
        print('tmp_list:',tmp_list)
        #real_data_tmp_folder = 'real_data_tmp_folder/' + username + '/' + project_name + '/' + "level"+str(tmp_level) + '/'
        if tmp_level == total_project_level:

            for file in tmp_list:
                #将所有文件传给project_owner
                '''
                 prefix_label = username + '/' + project_name + '/' + return_txt_name
                 destination = people_deal + '/' + project_name + '/' + return_txt_name
                 source_blob = storage.bucket.blob(prefix_label)
                 storage.bucket.copy_blob(source_blob, storage.bucket, destination)
                 storage.delete(f'{prefix_label}', token)
                '''
                prefix_label = username + '/' + project_name + '/' + file.split('.')[0]+'.txt'
                destination = project_owner_name + '/' + project_name + '/' + file.split('.')[0]+'.txt'
                source_blob = storage.bucket.blob(prefix_label)
                storage.bucket.copy_blob(source_blob, storage.bucket, destination)
                '''
                local_data_address = data_tmp_folder + file.name.split('/')[-1]
                project_owner_folder = storage.bucket.list_blobs(prefix=project_owner_name + '/' + project_name + '/' +file.split('.')[0] + '.txt')
                project_owner_folder.upload_from_filename(local_data_address)
                '''
                person_file_name = file.split('.')[0]
                if detail_file_of_project.objects.filter(annotator_name=username, project_name=project_name,
                                                         level_set=tmp_level - 1,
                                                         filename=person_file_name.split('/')[-1]).exists():
                    detail_file_of_project.objects.get(annotator_name=username, project_name=project_name,
                                                       level_set=tmp_level - 1,
                                                       filename=person_file_name.split('/')[-1]).delete()
                if ToDoList.objects.filter(project_name=project_name, annotator_name=username,
                                           file_name=person_file_name.split('/')[-1]).exists():
                    ToDoList.objects.get(project_name=project_name, annotator_name=username,
                                         file_name=person_file_name.split('/')[-1]).delete()
            shutil.rmtree(data_tmp_folder + "/")
            shutil.rmtree(real_data_tmp_folder + "/")
            shutil.rmtree(merge_data_tmp_folder + "/")
            project_data_list = detail_file_of_project.objects.filter(annotator_name=username,
                                                                      project_name=project_name).values_list('filename',
                                                                                                             flat=True)
            todo_list = ToDoList.objects.filter(annotator_name=username,
                                                project_name=project_name).values_list('file_name',
                                                                                       flat=True)

            return render(request, "annotator_show_project.html",
                          {"username": username, "project_name": project_name, "project_data_list": project_data_list,
                           "todo_list": todo_list})
        else:
            tmp_level+=1
            higher_level_annotator_name = project_detail.objects.filter(project_name=project_name,level_set=tmp_level).values_list('annotator_name',flat=True)
            print(higher_level_annotator_name)
            #files = os.listdir(data_tmp_folder)
            #files_count = len(files)
            files_count = len(tmp_list)
            files_per_person = math.floor(files_count / len(higher_level_annotator_name))
            remaining_files = files_count % len(higher_level_annotator_name)
            print('files_per_person', files_per_person)
            print('remaining_files', remaining_files)
            min_files_person = None
            min_files_count = float('inf')
            # 对于当前任务级别，找到拥有最少任务的人员

            for person in higher_level_annotator_name:
                records = detail_file_of_project.objects.filter(annotator_name=person,project_name=project_name,level_set=tmp_level).exists()
                if records == True:
                    person_files_count = len(detail_file_of_project.objects.filter(annotator_name=person,project_name=project_name,level_set=tmp_level))
                else:
                    person_files_count =0
                print('person',person)
                print('person_files_count', person_files_count)
                if person_files_count <= min_files_count:
                    min_files_count = person_files_count
                    min_files_person = person
                # 最后将 lowest_file_count_person 设为负责人
                people = min_files_person
                assigned_files = files_per_person
                if remaining_files > 0:
                    assigned_files += 1
                    remaining_files -= 1
            # 分派任务给负责人
                person_files = tmp_list[:assigned_files]
                print('people',people)
                print('这个人分配多少任务', len(person_files))
                for person_file in person_files:
                    prefix_label = username + '/' + project_name + '/' + person_file.split('.')[0]+'.txt'
                    destination = people + '/' + project_name + '/' + person_file.split('.')[0]+'.txt'
                    source_blob = storage.bucket.blob(prefix_label)
                    storage.bucket.copy_blob(source_blob, storage.bucket, destination)
                    person_file_name = person_file.split('.')[0]
                # 创建新的记录，标记负责人和任务
                    detail_file_of_project.objects.create(annotator_name=people, project_name=project_name,
                                                      level_set=tmp_level,
                                                      filename=person_file_name.split('/')[-1], people_sent=username)
                # 删除之前的记录
                    if detail_file_of_project.objects.filter(annotator_name=username, project_name=project_name,level_set=tmp_level - 1,filename=person_file_name.split('/')[-1]).exists():
                       detail_file_of_project.objects.get(annotator_name=username, project_name=project_name,
                                                   level_set=tmp_level - 1,
                                                   filename=person_file_name.split('/')[-1]).delete()
                    if ToDoList.objects.filter(project_name=project_name,annotator_name=username,file_name=person_file_name.split('/')[-1]).exists():
                        ToDoList.objects.get(project_name=project_name, annotator_name=username,
                                                              file_name=person_file_name.split('/')[-1]).delete()
                tmp_list = tmp_list[assigned_files:]

            '''
                        for _ in higher_level_annotator_name:
                            # 找到higher_level_annotator_name中filename最少的第一个人
                            # 根据 project_name 和 tmp_level 进行数据库查询，找到对应的记录
                            matching_records = detail_file_of_project.objects.filter(project_name=project_name, level_set=tmp_level)
                            print('matching_records:', matching_records)

                            # 初始化变量记录最少文件数量和对应的负责人
                            min_files_count = float('inf')  # 初始化为无穷大，确保第一个人肯定比它小
                            lowest_file_count_person = None

                            # 遍历查询到的记录，计算每个负责人的文件数量
                            for record in matching_records:
                                person_files_count = len(detail_file_of_project.objects.get(annotator_name=record.annotator_name,
                                                                                               project_name=project_name,
                                                                                               level_set=tmp_level))

                                if person_files_count < min_files_count or person_files_count==0:
                                    min_files_count = person_files_count
                                    lowest_file_count_person = record.annotator_name

                            # 最后将 lowest_file_count_person 设为负责人

                            people = lowest_file_count_person
                            assigned_files = files_per_person
                            if remaining_files > 0:
                                assigned_files += 1
                                remaining_files -= 1
                            #person_files = files[:assigned_files]
                            person_files = tmp_list[:assigned_files]
                            print('people:', people)
                            for person_file in person_files:
                                #person_file = person_file.split('.')[0]
                                #可能需要判断文件格式
                                prefix_label = username + '/' + project_name + '/' + person_file
                                destination = people + '/' + project_name + '/' + person_file
                                source_blob = storage.bucket.blob(prefix_label)
                                storage.bucket.copy_blob(source_blob, storage.bucket, destination)


                                #local_file_path = data_tmp_folder + "/" + person_file + ".txt"
                                #print(local_file_path)
                                #firebase_folder_path = people + "/" + project_name + "/" + person_file + ".txt"
                                #people_folder = storage.bucket.blob(firebase_folder_path)
                                #people_folder.upload_from_filename(local_file_path)
                                #people_folder.make_public()

                                #传给下个人之后删除

                                #folder_full_path = username+'/'+project_name+'/'+person_file + ".txt"
                                #storage.delete(f'{folder_full_path}', token)


                                person_file_name = person_file.split('.')[0]
                                detail_file_of_project.objects.create(annotator_name=people, project_name=project_name, level_set=tmp_level,
                                                                      filename=person_file_name.split('/')[-1],people_sent=username)
                                detail_file_of_project.objects.get(annotator_name=username, project_name=project_name,level_set=tmp_level-1,filename=person_file_name.split('/')[-1]).delete()
                            #files = files[assigned_files:]
                            tmp_list = tmp_list[assigned_files:]
            '''
            shutil.rmtree(data_tmp_folder + "/")
            shutil.rmtree(real_data_tmp_folder + "/")
            shutil.rmtree(merge_data_tmp_folder + "/")
            project_data_list = detail_file_of_project.objects.filter(annotator_name=username,
                                                                      project_name=project_name).values_list('filename',
                                                                                                             flat=True)
            todo_list = ToDoList.objects.filter(annotator_name=username,
                                                project_name=project_name).values_list('file_name',
                                                                                       flat=True)

            return render(request, "annotator_show_project.html",
                          {"username": username, "project_name": project_name, "project_data_list": project_data_list,
                           "todo_list": todo_list})
"""

class annotate_projectAPIView(APIView):
    def post(self,request,username,project_name):
        data = JSONParser().parse(request)
        # update：更新obj,每次点击，下载到real_data_tmp_folder
        tmp_level = project_detail.objects.get(annotator_name=username, project_name=project_name).level_set
        data_tmp_folder = 'data_tmp_folder/' + username + '/' + project_name + '/' + "level" + str(tmp_level) + '/'
        if not os.path.exists(data_tmp_folder):
            os.makedirs(data_tmp_folder)
        # real_data_tmp_folder用来存放obj文件，data_tmp_folder用来存放label文件
        real_data_tmp_folder = 'real_data_tmp_folder/' + username + '/' + project_name + '/' + "level" + str(
            tmp_level) + '/'
        if not os.path.exists(real_data_tmp_folder):
            os.makedirs(real_data_tmp_folder)
        merge_data_tmp_folder = 'merge_data_tmp_folder/' + username + '/' + project_name + '/' + "level" + str(
            tmp_level) + '/'
        if not os.path.exists(merge_data_tmp_folder):
            os.makedirs(merge_data_tmp_folder)
        # 下载得到原obj文件
        file_name = data.get('file_name')
        # file_name = file_name.split('.')[0]
        folder_name = project_detail.objects.filter(annotator_name=username, project_name=project_name)[0].folder_name
        prefix_data = "trained_dataset/" + folder_name + '/' + file_name + '.obj'
        #prefix_data = "all_dataset_folder/" + folder_name + '/' + file_name + '.obj'
        update_data = storage.bucket.blob(prefix_data)
        if tmp_level != 1:
            update_data.download_to_filename(real_data_tmp_folder + file_name + '.obj')
            # 之后需要删除
            # 下载上个一个人的label文件
            prefix_label = username + '/' + project_name + '/' + file_name + '.txt'
            update_label = storage.bucket.blob(prefix_label)
            update_label.download_to_filename(data_tmp_folder + file_name + '.txt')

            with open(real_data_tmp_folder+file_name+'.obj','r') as obj_file:
                obj_lines = obj_file.readlines()
            with open(data_tmp_folder + file_name + '.txt', 'r') as txt_file:
                txt_lines = txt_file.readlines()
            # 创建一个字典,将类别编号映射到颜色信息
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
            result_file_path = merge_data_tmp_folder + file_name + '.obj'
            with open(result_file_path, 'w') as result_file:
                i=0
                for line in obj_lines:
                    if line.startswith('v'):
                        idx = int(txt_lines[i].split()[1])
                        i+=1
                        color_info = color_mapping.get(idx, '[0.0, 0.0, 0.0]')
                        color_info = ', '.join(color_info.strip('[]').split(', '))
                        #new_line = f'{" ".join(line.split()[:4])} {color_info}\n'
                        new_line = f'{line.split()[0]} {line.split()[1]} {line.split()[2]} {line.split()[3]} {color_info}\n'
                        result_file.write(new_line)
        else:
            # tmp=1
            #update_data.download_to_filename(real_data_tmp_folder + file_name + '.obj')
            result_file_path = merge_data_tmp_folder + file_name + '.obj'
            update_data.download_to_filename(result_file_path)
        #response = FileResponse(open(result_file_path, 'rb'), as_attachment=True, filename=file_name + '.obj')
        #return response
        with open(result_file_path, 'rb') as result_file:
            file_content = result_file.read()

        return HttpResponse(file_content, content_type='application/octet-stream')
        """
        test_path= file_name+'.obj'
            # 获取到存储在后端项目中的 obj 文件的位置
        #obj_file_url = f'http://localhost:8001/{result_file_path}'
        #obj_file_url = static(result_file_path)
        obj_file_url= f'http://localhost:8001/statics/{test_path}'
            # 构建包含 obj 文件 URL 信息的字典
        response_data = {
            'message': 'Obj file processed successfully.',
            'obj_file_url': obj_file_url
        }
        # 使用 JsonResponse 返回 JSON 数据
        response = JsonResponse(response_data)
        response['Access-Control-Allow-Origin'] = '*'
        return response
        """

"""
def annotate_project(request, username, project_name):
    if request.method == 'POST':
        # update：更新obj,每次点击，下载到real_data_tmp_folder
        tmp_level = project_detail.objects.get(annotator_name=username, project_name=project_name).level_set
        data_tmp_folder = 'data_tmp_folder/' + username + '/' + project_name + '/' + "level"+str(tmp_level) + '/'
        if not os.path.exists(data_tmp_folder):
            os.makedirs(data_tmp_folder)
        #real_data_tmp_folder用来存放obj文件，data_tmp_folder用来存放label文件
        real_data_tmp_folder = 'real_data_tmp_folder/' + username + '/' + project_name + '/' + "level"+str(tmp_level) + '/'
        if not os.path.exists(real_data_tmp_folder):
            os.makedirs(real_data_tmp_folder)
        merge_data_tmp_folder = 'merge_data_tmp_folder/' + username + '/' + project_name + '/' + "level" + str(tmp_level) + '/'
        if not os.path.exists(merge_data_tmp_folder):
            os.makedirs(merge_data_tmp_folder)
        #下载得到原obj文件
        file_name = request.POST.get('file_name')
        #file_name = file_name.split('.')[0]
        folder_name = project_detail.objects.filter(annotator_name=username, project_name=project_name)[0].folder_name
        prefix_data = "all_dataset_folder/"+folder_name+'/'+file_name+'.obj'
        update_data = storage.bucket.blob(prefix_data)
        if tmp_level!=1:
            update_data.download_to_filename(real_data_tmp_folder+file_name+'.obj')
            #之后需要删除
            #下载上个一个人的label文件
            prefix_label = username+'/'+ project_name+'/'+ file_name+'.txt'
            update_label = storage.bucket.blob(prefix_label)
            update_label.download_to_filename(data_tmp_folder + file_name+'.txt')
            '''
            with open(real_data_tmp_folder+file_name+'.obj','r') as obj_file:
                obj_lines = obj_file.readlines()
            with open(data_tmp_folder + file_name + '.txt', 'r') as txt_file:
                txt_lines = txt_file.readlines()
            # 创建一个字典,将类别编号映射到颜色信息
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
            result_file_path = merge_data_tmp_folder + file_name + '.obj'
            with open(result_file_path, 'w') as result_file:
                i=0
                for line in obj_lines:
                    if line.startswith('v'):
                        idx = int(txt_lines[i].split()[1])
                        i+=1
                        color_info = color_mapping.get(idx, '[0.0, 0.0, 0.0]')
                        color_info = ', '.join(color_info.strip('[]').split(', '))
                        #new_line = f'{" ".join(line.split()[:4])} {color_info}\n'
                        new_line = f'{line.split()[0]} {line.split()[1]} {line.split()[2]} {line.split()[3]} {color_info}\n'
                        result_file.write(new_line)

            '''

        else:
            #tmp=1
            update_data.download_to_filename(real_data_tmp_folder + file_name + '.obj')
            #update_data.download_to_filename(merge_data_tmp_folder + file_name + '.obj')
        return render(request, "update_project.html",{"username": username, "project_name": project_name, "file_name": file_name, "folder_name": folder_name})
        #经过前端标注，将得到的label.txt下载到firebase 路径为username + '/' + project_name + '/' + filename
"""

class return_fileAPIView(APIView):
    def post(self, request,username,project_name):
        data = JSONParser().parse(request)
        return_txt_name = data.get('file_name')
        return_description = data.get('description')
        tmp_level = project_detail.objects.get(annotator_name=username, project_name=project_name).level_set
        merge_data_tmp_folder = 'merge_data_tmp_folder/' + username + '/' + project_name + '/' + "level" + str(
            tmp_level) + '/'
        if tmp_level == 1:
            full_path = merge_data_tmp_folder + return_txt_name + '.obj'
            os.remove(full_path)
            people_deal = Project_owner.objects.get(project_name=project_name).project_owner_name
            # 因为是level1，所以没有label.txt文件，此时return应该是删除任务之后告诉project-owner
            # ToDoList.objects.create(annotator_name=people_deal, project_name=project_name, file_name=return_txt_name, people_sent=username)
            project_owner_todolist.objects.create(project_owner=people_deal, todo_list_name=return_txt_name,
                                                  people_sent=username, project_name=project_name, description=return_description)
            # prefix_label = username + '/' + project_name + '/' + return_txt_name
            # destination = people_deal + '/' + project_name + '/' + return_txt_name
            # source_blob = storage.bucket.blob(prefix_label)
            # storage.bucket.copy_blob(source_blob, storage.bucket, destination)
            # storage.delete(f'{prefix_label}', token)
            detail_file_of_project.objects.get(annotator_name=username, project_name=project_name,
                                               filename=return_txt_name).delete()
            project_data_list = detail_file_of_project.objects.filter(annotator_name=username,
                                                                      project_name=project_name).values_list('filename',
                                                                                                             flat=True)
            todo_list = ToDoList.objects.filter(annotator_name=username,
                                                project_name=project_name).values_list('file_name',
                                                                                       flat=True)
            response_data = {
                'code': 201,
                'message': '返回任务',
                "username": username,
                "project_name": project_name,
                "project_data_list": project_data_list,
                "todo_list": todo_list
            }
            return JsonResponse(response_data, safe=False)

        else:
            # tmp_level-=1
            full_path = merge_data_tmp_folder + return_txt_name + '.obj'
            os.remove(full_path)
            people_deal = detail_file_of_project.objects.get(annotator_name=username, project_name=project_name,
                                                             filename=return_txt_name).people_sent
            ToDoList.objects.create(annotator_name=people_deal, project_name=project_name, file_name=return_txt_name,
                                    people_sent=username, description= return_description)
            prefix_label = username + '/' + project_name + '/' + return_txt_name + '.txt'
            destination = people_deal + '/' + project_name + '/' + return_txt_name + '.txt'
            source_blob = storage.bucket.blob(prefix_label)
            storage.bucket.copy_blob(source_blob, storage.bucket, destination)
            storage.delete(f'{prefix_label}', token)
            detail_file_of_project.objects.get(annotator_name=username, project_name=project_name,
                                               filename=return_txt_name).delete()
            project_data_list = detail_file_of_project.objects.filter(annotator_name=username,
                                                                      project_name=project_name).values_list('filename',
                                                                                                             flat=True)
            todo_list = ToDoList.objects.filter(annotator_name=username, project_name=project_name).values_list(
                'file_name', flat=True)
            response_data = {
                'code': 201,
                'message': '返回任务',
                "username": username,
                "project_name": project_name,
                "project_data_list": project_data_list,
                "todo_list": todo_list
            }
            return JsonResponse(response_data, safe=False)

'''
def return_file(request, username, project_name):
    if request.method == 'POST':
        return_txt_name = request.POST.get('file_name')
        tmp_level = project_detail.objects.get(annotator_name=username, project_name=project_name).level_set
        if tmp_level == 1:
            people_deal = Project_owner.objects.get(project_name=project_name).project_owner_name
            # 因为是level1，所以没有label.txt文件，此时return应该是删除任务之后告诉project-owner
            #ToDoList.objects.create(annotator_name=people_deal, project_name=project_name, file_name=return_txt_name, people_sent=username)
            project_owner_todolist.objects.create(project_owner=people_deal, todo_list_name=return_txt_name,people_sent=username,project_name=project_name)
            #prefix_label = username + '/' + project_name + '/' + return_txt_name
            #destination = people_deal + '/' + project_name + '/' + return_txt_name
            #source_blob = storage.bucket.blob(prefix_label)
            #storage.bucket.copy_blob(source_blob, storage.bucket, destination)
            #storage.delete(f'{prefix_label}', token)
            detail_file_of_project.objects.get(annotator_name=username, project_name=project_name,filename=return_txt_name).delete()
            project_data_list = detail_file_of_project.objects.filter(annotator_name=username,
                                                                      project_name=project_name).values_list('filename',
                                                                                                             flat=True)
            todo_list = ToDoList.objects.filter(annotator_name=username,
                                                project_name=project_name).values_list('file_name',
                                                                                       flat=True)
            return render(request, "annotator_show_project.html", {"username":username, "project_name":project_name, "project_data_list":project_data_list, "todo_list":todo_list})

        else:
            #tmp_level-=1
            people_deal = detail_file_of_project.objects.get(annotator_name=username, project_name=project_name, filename=return_txt_name).people_sent
            ToDoList.objects.create(annotator_name=people_deal, project_name=project_name, file_name=return_txt_name, people_sent=username)
            prefix_label = username + '/' + project_name + '/' + return_txt_name + '.txt'
            destination = people_deal + '/' + project_name + '/' + return_txt_name + '.txt'
            source_blob = storage.bucket.blob(prefix_label)
            storage.bucket.copy_blob(source_blob, storage.bucket, destination)
            storage.delete(f'{prefix_label}', token)
            detail_file_of_project.objects.get(annotator_name=username, project_name=project_name, filename=return_txt_name).delete()
            project_data_list = detail_file_of_project.objects.filter(annotator_name=username,project_name=project_name).values_list('filename',flat=True)
            todo_list = ToDoList.objects.filter(annotator_name=username,project_name=project_name).values_list('file_name',flat=True)
            return render(request, "annotator_show_project.html",
                          {"username": username, "project_name": project_name, "project_data_list": project_data_list,
                           "todo_list": todo_list})

'''
#delete：return



