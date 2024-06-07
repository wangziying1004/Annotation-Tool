import os

from django.shortcuts import render, redirect
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib import messages
from .models import Model_Info
from manager.models import Manager_UserInfo
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
import pyrebase
from .serializers import Model_InfoSerializer

Config = {
  "apiKey": "AIzaSyB9d_LpVH9A9OU82xqp0Fuo-XhhjQMbksI",
  "authDomain": "ndc-annotation-tool.firebaseapp.com",
  "projectId": "ndc-annotation-tool",
  "storageBucket": "ndc-annotation-tool.appspot.com",
  "messagingSenderId": "30054694568",
  "appId": "1:30054694568:web:3a4900a7430212fcab8c9d",
  "measurementId": "G-MGCTELM2B1",
  "serviceAccount": "model_application/ndc-annotation-tool-firebase-adminsdk.json",
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

# Create your views here.
class Add_modelView(APIView):
    def post(self, request,manager_username):
        data = JSONParser().parse(request)
        folder_name = data.get('folderName')
        if folder_name:
            model_info = Model_Info.objects.create(model_name=folder_name, manager_name=manager_username)
            return JsonResponse({'message': 'Model add successfully'}, status=204)
        else:
            return JsonResponse({'message': 'No folder name provided'}, status=400)

    def get(self, request, manager_username):
        model = Model_Info.objects.all()
        serializer = Model_InfoSerializer(model, many=True)
        return JsonResponse(serializer.data, safe=False)

class Delete_modelView(APIView):
    def delete(self, request, manager_username):
        data = JSONParser().parse(request)
        path = data.get('folderName')
        all_model_folder = 'all_model_folder'
        model_full_path = os.path.join(all_model_folder, path)
        # path="dataset_test"
        dir_content = storage.bucket.list_blobs(prefix=model_full_path)
        print(dir_content)
        for file in dir_content:
            storage.delete(file.name, token)
        Model_Info.objects.filter(model_name=path).delete()
        return JsonResponse({'message': 'Model delete successfully'}, status=204)
    def get(self, request, manager_username):
        dataset = Model_Info.objects.all()
        serializer = Model_InfoSerializer(dataset, many=True)
        return JsonResponse(serializer.data, safe=False)

class ShowModelView(APIView):
    def get(self, request, manager_username):
        model = Model_Info.objects.all()
        serializer = Model_InfoSerializer(model, many=True)
        return JsonResponse(serializer.data, safe=False)

class UpdateModelView(APIView):
    def put(self, request, manager_username):
        data = JSONParser().parse(request)
        folder_name = data.get('folderName')
        return JsonResponse({'folder_name': folder_name})
        #return redirect('show_exact_model', manager_username=manager_username, folder_name=folder_name)

    def get(self, request, manager_username):
        model = Model_Info.objects.all()
        serializer = Model_InfoSerializer(model, many=True)
        return JsonResponse(serializer.data, safe=False)

class ShowExactModelView(APIView):
    def get(self, request, manager_username, folder_name):
        all_model_folder = 'all_model_folder'
        folder_full_path = os.path.join(all_model_folder, folder_name)
        dir_content = storage.bucket.list_blobs(prefix=folder_full_path)
        filelist = [file.name for file in dir_content]
        return JsonResponse({'manager_username': manager_username, 'folder_name': folder_name, 'filelist': filelist})

class DeleteExactModelView(APIView):
    def delete(self, request, manager_username, folder_name):
        data = JSONParser().parse(request)
        all_model_folder = 'all_model_folder'
        folder_full_path = os.path.join(all_model_folder, folder_name)
        file_name_all = data.get('file_name')
        file_name_parts = file_name_all.split('/')
        file_name = file_name_parts[-1]
        #print('test')
        # dir_content = storage.bucket.list_blobs(prefix=folder_name)

        storage.delete(f'{folder_full_path}/{file_name}', token)
        #return redirect('show_exact_data', manager_username=manager_username, folder_name=folder_name)
        return JsonResponse({'message': 'Exact model_file delete successfully'}, status=204)


"""
def add_model(request, username):
    if request.method == 'POST':
        print('test')
        model_name = request.POST.get('modelName')
        print('test2')
        print(model_name)
        if model_name:
            model_info = Model_Info.objects.create(model_name=model_name, manager_name=username)
            messages.success(request, "model information saved successfully.")
            return render(request, 'add_model.html', {'username': username})
        else:
            messages.error(request, "model name is required.")

    return render(request, 'add_model.html', {'username': username})


def del_model(request, username):
    if request.method == 'POST':
        # folder_name = request.POST.get('folderName')
        # storage.delete()
        # ref = storage.child('dataset_test')
        # test = storage.bucket()
        # print(ref)
        # print(test)
        all_model_folder='all_model_folder'
        path = request.POST.get('modelName')
        model_full_path = os.path.join(all_model_folder, path)
        print(model_full_path)
        # path="dataset_test"
        #dir_content = storage.bucket.list_blobs(prefix='all_models_folder/')
        #print(dir_content)
        #for file in dir_content:
        storage.delete(model_full_path, token)
        Model_Info.objects.filter(model_name=path).delete()
        return redirect('del_model', username=username)
    else:
        model_infos = Model_Info.objects.all()
        # 提取所有对象的 filename 属性
        modelnames = [info.model_name for info in model_infos]
        return render(request, 'del_model.html', {'username': username, 'modelnames': modelnames})


def show_model(request, username):
    if request.method == 'POST':
        # 获取所有的 Dataset_Info 对象
        model_infos = Model_Info.objects.all()
        # 提取所有对象的 filename 属性
        modelnames = [info.model_name for info in model_infos]
        return render(request, 'show_models.html', {'username': username, 'modelnames': modelnames})
    return render(request, 'show_models.html', {'username': username})

"""

