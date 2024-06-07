from django.db import models

# Create your models here.
class Model_Info(models.Model):
    model_name = models.CharField(max_length=50)
    manager_name = models.CharField(max_length=30)