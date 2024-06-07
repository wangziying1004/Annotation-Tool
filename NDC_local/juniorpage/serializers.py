from rest_framework import serializers
from .models import project_level
from .models import ToDoList
from .models import detail_file_of_project

class ProjectLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = project_level
        fields = '__all__'

class ToDoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDoList
        fields = '__all__'

class detail_file_of_projectSerializer(serializers.ModelSerializer):
    class Meta:
        model = detail_file_of_project
        fields = '__all__'
