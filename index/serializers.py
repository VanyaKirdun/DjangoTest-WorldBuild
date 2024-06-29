from rest_framework import serializers
from .models import Worker, PositionList, BuildObject, Client

class WorkerSerializer(serializers.ModelSerializer):
  class Meta:
    model = Worker
    fields = '__all__'
    
class PositionListSerializer(serializers.ModelSerializer):
  class Meta:
    model = PositionList
    fields = '__all__'
  
class BuildObjectSerializer(serializers.ModelSerializer):
  class Meta:
    model = BuildObject
    fields = '__all__'
    
class ClientsSerializer(serializers.ModelSerializer):
  class Meta:
    model = Client
    fields = '__all__'