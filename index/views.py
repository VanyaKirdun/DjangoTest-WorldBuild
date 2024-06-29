from django.shortcuts import render
from rest_framework import viewsets
from index.models import Worker, PositionList, BuildObject, Client
from index.serializers import WorkerSerializer, PositionListSerializer, BuildObjectSerializer, ClientsSerializer
from django.http import HttpResponse
from django.forms.models import model_to_dict
from index.scripts.calcSalary import calcSalary


class WorkerApiView(viewsets.ModelViewSet):
  queryset = Worker.objects.all()
  serializer_class = WorkerSerializer
  
class PositionListApiView(viewsets.ModelViewSet):
  queryset = PositionList.objects.all()
  serializer_class = PositionListSerializer
  
class BuildObjectApiView(viewsets.ModelViewSet):
  queryset = BuildObject.objects.all()
  serializer_class = BuildObjectSerializer
  
class ClientsApiView(viewsets.ModelViewSet):
  queryset = Client.objects.all()
  serializer_class = ClientsSerializer


def salary(request):
  
  workers = Worker.objects.all()
  buildObject = BuildObject.objects.all()
  queryset = {}
  for item in workers:
    workedHoursData = item.timeWork[f'{request.GET['year']}'][f'{request.GET['mounth']}']['data']
    positionSalary = PositionList.objects.all()[item.position-1].salaryOfTime
    totalSalary = calcSalary(workedHoursData, buildObject, positionSalary)
    
    
    queryset[item.id] = {
      'worker': model_to_dict(item),
      'salary': totalSalary
    }
      
  return HttpResponse(f"{queryset}")
  