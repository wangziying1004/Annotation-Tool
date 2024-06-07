from django.db import models

# Create your models here.
class UserInfo(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=20)
    #user_type = models.CharField(max_length=20, default="annotator")
    age = models.IntegerField(default=30)
    email = models.EmailField(default="<123@gmail.com>")
