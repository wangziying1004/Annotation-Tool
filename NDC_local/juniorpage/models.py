from django.db import models
from datetime import datetime
from django.utils import timezone
# Create your models here.
class File(models.Model):
    supervisor = models.CharField(max_length=32)
    myname = models.CharField(max_length=32, default="")
    filename = models.FileField(upload_to='obj_url', name='file_address') # Uploaded file

class project_level(models.Model):
    annotator_name = models.CharField(max_length=32, default='')
    project_name = models.CharField(max_length=50)
    level_set = models.IntegerField(default=1)
    project_start_date = models.DateTimeField(default=timezone.now)
    folder_name = models.CharField(max_length=30,default='')


class ToDoList(models.Model):
    annotator_name = models.CharField(max_length=32, default='')
    people_sent = models.CharField(max_length=30,default='')
    project_name = models.CharField(max_length=50, default='')
    file_name = models.CharField(max_length=50, default='')
    project_change_date = models.DateField(default=timezone.now)
    description = models.TextField(default='')

class detail_file_of_project(models.Model):
    annotator_name = models.CharField(max_length=32, default='')
    project_name = models.CharField(max_length=50, default='')
    level_set = models.IntegerField(default=1)
    filename = models.CharField(max_length=32, default='')
    people_sent = models.CharField(max_length=30,default='')
    #folder_name = models.CharField(max_length=30,default='')
