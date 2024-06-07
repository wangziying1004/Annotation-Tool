"""
URL configuration for NDC_local project.

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
from loginpage import views as loginpage_views
from juniorpage import views as juniorpage_views
from project_owner_page import views as project_owner_views
from rest_framework.documentation import include_docs_urls
urlpatterns = [
    path("docs/", include_docs_urls(title='My API title')),
    path("loginpage/",loginpage_views.adminstratorAPIView.as_view()),
    path("signup/",loginpage_views.Junior_signupAPIView.as_view(),name='junior_signup'),
    path("annotatorpage/<str:username>/", juniorpage_views.juniorfunctionAPIView.as_view(), name='annotator_user_functions'),
    path("annotatorpage/<str:username>/<str:project_name>/show/", juniorpage_views.show_projectAPIView.as_view(),name='show_project_functions'),
    path("annotatorpage/<str:username>/<str:project_name>/annotate/", juniorpage_views.annotate_projectAPIView.as_view(),name='annotate_project'),
    path("annotatorpage/<str:username>/<str:project_name>/return/", juniorpage_views.return_fileAPIView.as_view(), name='return_file'),
    path('project_owner/<str:username>/', project_owner_views.ownerfunctionAPIView.as_view(), name='project_owner_functions'),
    path('project_owner/<str:username>/startproject/', project_owner_views.PretrainAPIView.as_view(), name='pretrain'),
    path('project_owner/<str:username>/startproject/<str:project_name>/levelandtask/',project_owner_views.startproject_setlevelandtaskAPIView.as_view(), name='startproject_setlevelandtask'),
    path('project_owner/<str:username>/startproject/<str:project_name>/assignpeople/',project_owner_views.startproject_assignpeopleAPIView.as_view(), name='startproject_assignpeople'),
    path('project_owner/<str:username>/<str:project_name>/', project_owner_views.show_projectAPIView.as_view(), name='show_project'),
    path('project_owner/<str:username>/<str:project_name>/deleted/', project_owner_views.end_projectAPIView.as_view(),name='end_project'),
    path('project_owner/<str:username>/<str:project_name>/export/', project_owner_views.export_projectAPIView.as_view(),name='export_project'),

]
"""
    path("admin/", admin.site.urls),
    #path("",loginpage_views.primarypage),
    path("loginpage/",loginpage_views.administrator),
    path("signup/",loginpage_views.junior_signup, name='junior_signup'),
    path("annotatorpage/<str:username>/", juniorpage_views.juniorfunction, name='annotator_user_functions'),
    path("annotatorpage/<str:username>/<str:project_name>/show/",juniorpage_views.show_project, name='show_project_functions'),
    path("annotatorpage/<str:username>/<str:project_name>/annotate/",juniorpage_views.annotate_project, name='annotate_project'),
    path("annotatorpage/<str:username>/<str:project_name>/return/",juniorpage_views.return_file, name='return_file'),
    path('project_owner/<str:username>/', project_owner_views.ownerfunction,name='project_owner_functions'),
    path('project_owner/<str:username>/startproject/', project_owner_views.pretrain, name='pretrain'),
    path('project_owner/<str:username>/startproject/<str:project_name>/levelandtask/', project_owner_views.startproject_setlevelandtask, name='startproject_setlevelandtask'),
    path('project_owner/<str:username>/startproject/<str:project_name>/assignpeople/', project_owner_views.startproject_assignpeople, name='startproject_assignpeople'),
    path('project_owner/<str:username>/<str:project_name>/',project_owner_views.show_project, name='show_project'),
    path('project_owner/<str:username>/<str:project_name>/deleted/',project_owner_views.end_project, name='end_project'),
    path('project_owner/<str:username>/<str:project_name>/export/', project_owner_views.export_project, name='export_project'),
"""