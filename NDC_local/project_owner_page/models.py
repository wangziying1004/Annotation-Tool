from datetime import datetime
from django.utils import timezone
from django.db import models

# Create your models here.
class Project_owner(models.Model):
    project_owner_name = models.CharField(max_length=30)
    project_name = models.CharField(max_length=30)
    status = models.BooleanField(default=True)
    project_start_date = models.DateTimeField(default=timezone.now)
    project_level = models.IntegerField(default=2)
    project_max_tasks = models.IntegerField(default=10)
    folder_name = models.CharField(max_length=30,default='')

class TodoList(models.Model):
    project_owner = models.CharField(max_length=30)
    todo_list_name = models.CharField(max_length=30)
    people_sent = models.CharField(max_length=30,default='')
    project_name = models.CharField(max_length=30,default='')
    description = models.TextField(default='')
    #todo_list_description = models.CharField(max_length=200)



