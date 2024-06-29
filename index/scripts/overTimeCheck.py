from django.shortcuts import render
from rest_framework import viewsets
from index.models import Worker, PositionList, BuildObject
from index.serializers import WorkerSerializer
from django.http import HttpResponse
from django.forms.models import model_to_dict
from datetime import datetime, timedelta
from calendar import monthrange
import json

      
def overTimeCheck(request):
  mounthCount = 1
  match request.GET['mounth']:
    case 'january':
      mounthCount = 1
    case 'february':
      mounthCount = 2
    case 'march':
      mounthCount = 3
    case 'april':
      mounthCount = 4
    case 'may':
      mounthCount = 5
    case 'june':
      mounthCount = 6
    case 'july':
      mounthCount = 7
    case 'august':
      mounthCount = 8
    case 'september':
      mounthCount = 9
    case 'october':
      mounthCount = 10
    case 'november':
      mounthCount = 11
    case 'december':  
      mounthCount = 12
      
  mounthMaxDay = monthrange(int(request.GET['year']), mounthCount)[1]
  start_date_str = f"{request.GET['year']}-{mounthCount}-{1}"
  end_date_str = f"{request.GET['year']}-{mounthCount}-{mounthMaxDay}"

  # Преобразование строк в объекты даты
  start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
  end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

  # Подсчет рабочих дней
  current_date = start_date
  working_days = 0

  while current_date <= end_date:
      if current_date.weekday() < 5:  # Понедельник-пятница считаются рабочими днями
          working_days += 1
      current_date += timedelta(days=1)

  workers = Worker.objects.all()
  queryset = {}
  for item in workers:
    positionsDayHours = PositionList.objects.all()[item.position-1].timeWorkByDay
    requaredHours = positionsDayHours*working_days
    workedHoursData = item.timeWork[f'{request.GET['year']}'][f'{request.GET['mounth']}']['data']
    
    workedHours = 0
    for key in workedHoursData:
      for indexKey in workedHoursData[key]:
        workedHours += int(workedHoursData[key][indexKey])
      
    if requaredHours > workedHours:
      queryset[item.id] = {
        'worker': model_to_dict(item),
        'overTimes': workedHours - requaredHours
      }
      print(queryset)
    elif requaredHours < workedHours:
      queryset[item.id] = {
        'worker': model_to_dict(item),
        'overTimes': workedHours - requaredHours
      }
    elif requaredHours == workedHours:
      queryset[item.id] = {
        'worker': model_to_dict(item),
        'overTimes': 0
      }
  return HttpResponse(f"{queryset}")
     