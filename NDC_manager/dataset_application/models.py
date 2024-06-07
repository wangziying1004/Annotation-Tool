from django.db import models
from manager.models import models as manager_model
from manager.models import Manager_UserInfo
# Create your models here.
class Dataset_Info(models.Model):
    #data_name = models.CharField(max_length=30)
    #data_url = models.URLField()
    filename = models.CharField(max_length=30)  # Uploaded file
    manager_name = models.CharField(max_length=30)