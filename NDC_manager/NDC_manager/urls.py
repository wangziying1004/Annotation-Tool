"""
URL configuration for NDC_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from manager import views as manager_views
from dataset_application import views as dataset_views
from model_application import views as model_views
from rest_framework.documentation import include_docs_urls
urlpatterns = [
    #path("", admin.site.urls),
    path("docs/", include_docs_urls(title='My API title')),
    path("managerloginpage/", manager_views.AdministratorAPIView.as_view(), name="managerloginpage"),
    path("managerpage/<str:manager_username>/", manager_views.FunctionsAPIView.as_view(), name='user_functions'),  # 新增个人界面URL
    #path("managerpage/<str:manager_username>/add_account/", manager_views.AddUserInfoView.as_view(), name='add_functions'),
    path("managerpage/<str:manager_username>/delete_account/", manager_views.DeleteUserInfoView.as_view(), name='del_functions'),
    path("managerpage/<str:manager_username>/show_account/", manager_views.ShowUserInfoView.as_view(), name='show_functions'),
    path("managerpage/<str:manager_username>/update_account/", manager_views.UpdateUserInfoView.as_view(), name='update_functions'),
    path("managerpage/<str:manager_username>/add_dataset/", dataset_views.Add_DatasetAPIView.as_view(), name='add_dataset2'),
    path("managerpage/<str:manager_username>/del_dataset/", dataset_views.Delete_DatasetAPIView.as_view(), name='del_dataset'),
    path("managerpage/<str:manager_username>/show_dataset/", dataset_views.ShowDatasetAPIView.as_view(), name='show_dataset'),
    path("managerpage/<str:manager_username>/update_dataset/", dataset_views.UpdateDatasetAPIView.as_view(), name='update_dataset'),
    path("managerpage/<str:manager_username>/update_dataset/<str:folder_name>/", dataset_views.ShowExactDataAPIView.as_view(), name='show_exact_data'),
    path("managerpage/<str:manager_username>/update_dataset/<str:folder_name>/deleted/", dataset_views.DeleteExactDataAPIView.as_view(), name='delete_exact_data'),
    path("managerpage/<str:manager_username>/add_model/", model_views.Add_modelView.as_view(), name='add_model'),
    path("managerpage/<str:manager_username>/del_model/", model_views.Delete_modelView.as_view(), name='del_model'),
    path("managerpage/<str:manager_username>/show_model/", model_views.ShowModelView.as_view(), name='show_model'),
    path("managerpage/<str:manager_username>/update_model/", model_views.UpdateModelView.as_view(),name='update_model'),
    path("managerpage/<str:manager_username>/update_model/<str:folder_name>/", model_views.ShowExactModelView.as_view(),name='show_exact_model'),
    path("managerpage/<str:manager_username>/update_model/<str:folder_name>/deleted/", model_views.DeleteExactModelView.as_view(), name='delete_exact_model'),

    #path("", manager_views.primarypage),
    #path("managerloginpage/", manager_views.administrator, name="managerloginpage"),
    #path("managerpage/<str:username>/", manager_views.functions, name='user_functions'),  # 新增个人界面URL
    #path("managerpage/<str:username>/add_account/", manager_views.add_functions, name='add_functions'),
    #path("managerpage/<str:username>/delete_account/", manager_views.del_functions, name='del_functions'),
    #path("managerpage/<str:username>/show_account/", manager_views.show_functions, name='show_functions'),
    #path("managerpage/<str:username>/update_account/", manager_views.update_functions, name='update_functions'),
    #path("managerpage/<str:username>/add_dataset/", dataset_views.add_dataset2, name='add_dataset2'),
    #path("managerpage/<str:username>/del_dataset/", dataset_views.del_dataset, name='del_dataset'),
    #path("managerpage/<str:username>/show_dataset/", dataset_views.show_dataset, name='show_dataset'),
    #path("managerpage/<str:username>/update_dataset/", dataset_views.update_dataset, name='update_dataset'),
    #path("managerpage/<str:username>/update_dataset/<str:folder_name>", dataset_views.show_exact_data, name='show_exact_data'),
    #path("managerpage/<str:username>/update_dataset/<str:folder_name>/added", dataset_views.add_exact_data, name='add_exact_data'),
    #path("managerpage/<str:username>/update_dataset/<str:folder_name>/deleted", dataset_views.delete_exact_data, name='delete_exact_data'),
    #path("managerpage/<str:username>/add_model/", model_views.add_model, name='add_model'),
    #path("managerpage/<str:username>/del_model/", model_views.del_model, name='del_model'),
    #path("managerpage/<str:username>/show_model/", model_views.show_model, name='show_model'),


]
