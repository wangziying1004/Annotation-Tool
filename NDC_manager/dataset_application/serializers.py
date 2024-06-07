from rest_framework import serializers
from .models import Dataset_Info

class Dataset_InfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset_Info
        fields = '__all__'  # 或者指定你想要序列化的字段，比如 ['filename', 'manager_name']
