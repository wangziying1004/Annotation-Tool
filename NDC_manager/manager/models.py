from django.db import models

# Create your models here.
class Manager_UserInfo(models.Model):
    Manager_username = models.CharField(max_length=32)
    Manager_password = models.CharField(max_length=20)
    Manager_age =models.IntegerField(default=30)
    Manager_email = models.EmailField(default="<123@gmail.com>")


class UserInfo(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=20)
    age = models.IntegerField(default=30)
    email = models.EmailField(default="<123@gmail.com>")
    #user_type = models.CharField(max_length=10, default="junior")
    # 其他字段...

    class Meta:
        # 指定该模型使用另一个数据库
        app_label = 'loginpage'