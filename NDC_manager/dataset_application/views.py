from django.shortcuts import render, redirect
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib import messages
from .models import Dataset_Info
from manager.models import Manager_UserInfo
import pyrebase
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
import firebase_admin
from firebase_admin import storage as admin_storage, credentials, firestore
#from google.cloud import storage as blob_storage
import os

from .serializers import Dataset_InfoSerializer

Config = {
  "apiKey": "AIzaSyB9d_LpVH9A9OU82xqp0Fuo-XhhjQMbksI",
  "authDomain": "ndc-annotation-tool.firebaseapp.com",
  "projectId": "ndc-annotation-tool",
  "storageBucket": "ndc-annotation-tool.appspot.com",
  "messagingSenderId": "30054694568",
  "appId": "1:30054694568:web:3a4900a7430212fcab8c9d",
  "measurementId": "G-MGCTELM2B1",
  "serviceAccount": "dataset_application/ndc-annotation-tool-firebase-adminsdk.json",
  "databaseURL": ""
}

firebase = pyrebase.initialize_app(Config)
storage = firebase.storage()
#client_id='firebase-adminsdk-3fsny'
#auth = firebase.auth()
#cred = credentials.Certificate("dataset_application/ndc-annotation-tool-firebase-adminsdk.json")
#firebase_admin.initialize_app(cred)
#custom_token = auth.create_custom_token(client_id)
#storage_client = blob_storage.Client()
#bucket = storage_client.get_bucket('gs://ndc-annotation-tool.appspot.com')
auth = firebase.auth()
email='wangziying116@gmail.com'
password='password1004'
# Log the user in
user = auth.sign_in_with_email_and_password(email, password)
# before the 1 hour expiry:
user = auth.refresh(user['refreshToken'])
# now we have a fresh token
token=user['idToken']
"""
def add_dataset(request, username):
  if request.method == 'POST':
    if 'dataset' in request.FILES:
      folder = request.FILES.getlist('dataset')
      folder_name = request.POST.get('folderName')
      print(folder_name)# 获取文件夹名称参数
      dataset_info = Dataset_Info.objects.create(filename=folder_name, manager_name=username)
      for file in folder:
        # 上传文件夹中的每个文件到 Firebase 存储
      #f"{folder_name}/"
        #print(file.name)
        file_save = default_storage.save(file.name, file)
        file_full_path = os.path.join(settings.MEDIA_ROOT, file_save)
        #print(file_full_path)
        # 设置存储路径为 文件夹名/文件名
        storage.child(f"{folder_name}/"+file.name).put(file_full_path)
        delete = default_storage.delete(file.name)

      messages.success(request, "File upload in Firebase Storage successful")
      return render(request, 'add_dataset.html',
                    {'username': username, 'success_msg': 'File upload in Firebase Storage successful'})
    else:
      messages.error(request, "No dataset uploaded")
      return render(request, 'add_dataset.html', {'username': username, 'error_msg': 'No dataset uploaded'})
  return render(request, 'add_dataset.html', {'username': username})
"""

class Add_DatasetAPIView(APIView):
  def post(self,request,manager_username):
      data = JSONParser().parse(request)
      folder_name = data.get('folderName')
      if folder_name:
        dataset_info = Dataset_Info.objects.create(filename=folder_name, manager_name=manager_username)
        return JsonResponse({'message': 'Dataset add successfully'}, status=204)
      else:
        return JsonResponse({'message': 'No folder name provided'}, status=400)
  def get(self,request,manager_username):
      dataset=Dataset_Info.objects.all()
      serializer = Dataset_InfoSerializer(dataset,many=True)
      return JsonResponse(serializer.data,safe=False)

class Delete_DatasetAPIView(APIView):
  def delete(self,request,manager_username):
      data = JSONParser().parse(request)
      path =data.get('folderName')
      all_dataset_folder = 'all_dataset_folder'
      dataset_full_path = os.path.join(all_dataset_folder, path)
      # path="dataset_test"
      dir_content = storage.bucket.list_blobs(prefix=dataset_full_path)
      print(dir_content)
      for file in dir_content:
          storage.delete(file.name, token)
      Dataset_Info.objects.filter(filename=path).delete()
      return JsonResponse({'message': 'Dataset delete successfully'}, status=204)
  def get(self,request,manager_username):
      dataset = Dataset_Info.objects.all()
      serializer = Dataset_InfoSerializer(dataset, many=True)
      return JsonResponse(serializer.data, safe=False)

class ShowDatasetAPIView(APIView):
    def get(self, request, manager_username):
        dataset = Dataset_Info.objects.all()
        serializer = Dataset_InfoSerializer(dataset, many=True)
        return JsonResponse(serializer.data, safe=False)

class UpdateDatasetAPIView(APIView):
    def put(self, request, manager_username):
        data = JSONParser().parse(request)
        folder_name = data.get('folderName')
        return JsonResponse({'folder_name': folder_name})
        #return redirect('show_exact_data', manager_username=manager_username, folder_name=folder_name)
        #我不太清楚哪种方法对前端更友好
    def get(self, request, manager_username):
        dataset = Dataset_Info.objects.all()
        serializer = Dataset_InfoSerializer(dataset, many=True)
        return JsonResponse(serializer.data, safe=False)

class ShowExactDataAPIView(APIView):
    def get(self, request, manager_username, folder_name):
        all_dataset_folder = 'all_dataset_folder'
        folder_full_path = os.path.join(all_dataset_folder, folder_name)
        dir_content = storage.bucket.list_blobs(prefix=folder_full_path)
        filelist = [file.name for file in dir_content]
        return JsonResponse({'manager_username': manager_username, 'folder_name': folder_name, 'filelist': filelist})

class AddExactDataAPIView(APIView):
    def post(self, request, manager_username, folder_name):
        return None
class DeleteExactDataAPIView(APIView):
    def delete(self, request, manager_username, folder_name):
        data = JSONParser().parse(request)
        all_dataset_folder = 'all_dataset_folder'
        folder_full_path = os.path.join(all_dataset_folder, folder_name)
        file_name_all = data.get('file_name')
        file_name_parts = file_name_all.split('/')
        file_name = file_name_parts[-1]
        #print('test')
        # dir_content = storage.bucket.list_blobs(prefix=folder_name)
        storage.delete(f'{folder_full_path}/{file_name}', token)
        #return redirect('show_exact_data', manager_username=manager_username, folder_name=folder_name)
        return JsonResponse({'message': 'Exact Data delete successfully'}, status=204)


"""
def add_dataset2(request, username):
  if request.method == 'POST':
    folder_name = request.POST.get('folderName')
    print('test')
    print(folder_name)
    if folder_name:
      dataset_info = Dataset_Info.objects.create(filename=folder_name, manager_name=username)
      messages.success(request, "Dataset information saved successfully.")
      return render(request, 'add_dataset2.html', {'username': username})
    else:
      messages.error(request, "Folder name is required.")

  return render(request, 'add_dataset2.html', {'username': username})

def del_dataset(request, username):
  if request.method == 'POST':
    #folder_name = request.POST.get('folderName')
    #storage.delete()
    #ref = storage.child('dataset_test')
    #test = storage.bucket()
    #print(ref)
    #print(test)
    all_dataset_folder = 'all_dataset_folder'
    path = request.POST.get('folderName')
    dataset_full_path = os.path.join(all_dataset_folder, path)
    #path="dataset_test"
    dir_content = storage.bucket.list_blobs(prefix=dataset_full_path)
    print(dir_content)
    for file in dir_content:
      storage.delete(file.name,token)
    Dataset_Info.objects.filter(filename=path).delete()
    return redirect('del_dataset', username=username)
  else:
    dataset_infos = Dataset_Info.objects.all()
    # 提取所有对象的 filename 属性
    filenames = [info.filename for info in dataset_infos]
    return render(request,'del_dataset.html',{'username': username, 'filenames': filenames})

def show_dataset(request, username):
    #folder = storage.list_files(prefiex="/")
    #print(folder)
    #for files in folder:
    #  print(files.name)
    if request.method == 'POST':
      # 获取所有的 Dataset_Info 对象
      dataset_infos = Dataset_Info.objects.all()
      # 提取所有对象的 filename 属性
      filenames = [info.filename for info in dataset_infos]
      return render(request, 'show_dataset.html', {'username': username, 'filenames': filenames})
    return render(request, 'show_dataset.html', {'username': username})

def update_dataset(request, username):
  if request.method == 'POST':
    #all_dataset_folder = 'all_dataset_folder'
    folder_name = request.POST.get('folderName')
    #folder_full_path = os.path.join(all_dataset_folder, folder_name)
    #dir_content = storage.bucket.list_blobs(prefix=folder_name)
    #filelist = [file.name for file in dir_content]
    #print(folder_full_path)
    return redirect('show_exact_data', username=username, folder_name=folder_name)
  else:
    dataset_infos = Dataset_Info.objects.all()
    # 提取所有对象的 filename 属性
    folder_list = [info.filename for info in dataset_infos]
    return render(request, 'update_dataset.html', {'username': username, 'folder_list': folder_list})

def show_exact_data(request, username,folder_name):
  all_dataset_folder = 'all_dataset_folder'
  folder_full_path = os.path.join(all_dataset_folder, folder_name)
  dir_content = storage.bucket.list_blobs(prefix=folder_full_path)
  filelist = [file.name for file in dir_content]
  return render(request, 'show_exact_data.html',
                {'username': username, 'folder_name': folder_name, 'filelist': filelist})
"""
"""
def add_exact_data(request, username,folder_name):
  return None

def delete_exact_data(request, username,folder_name):
  all_dataset_folder = 'all_dataset_folder'
  folder_full_path = os.path.join(all_dataset_folder, folder_name)
  file_name_all = request.POST.get('file_name')
  file_name_parts = file_name_all.split('/')
  file_name = file_name_parts[-1]
  print('test')
  #dir_content = storage.bucket.list_blobs(prefix=folder_name)

  storage.delete(f'{folder_full_path}/{file_name}', token)
  return redirect('show_exact_data', username=username, folder_name=folder_name)
  #return render(request,'show_exact_data.html',{'username': username, 'folder_name':folder_name})
"""