from rest_framework import serializers
from .models import Project_owner
from .models import TodoList
class TodoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoList
        fields = '__all__'

class ProjectOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project_owner
        fields = '__all__'