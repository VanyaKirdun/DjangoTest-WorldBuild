from django.db import models

class Worker(models.Model):
  id = models.CharField('id', max_length=50, primary_key=True)
  name = models.CharField(max_length=50)
  tel = models.IntegerField()
  position = models.IntegerField()
  timeWork = models.JSONField()
  login = models.CharField(max_length=50, default=f'{name}{id}')
  password = models.CharField(max_length=50, default=name)
  def __str__(self):
    return f'{self.pk}) {self.name}'
  
class Client(models.Model):
  id = models.CharField('id', max_length=50, primary_key=True)
  name = models.CharField(max_length=50)
  tel = models.IntegerField()
  objectsData = models.JSONField()
  def __str__(self):
    return f'{self.pk}) {self.name}'
  
class BuildObject(models.Model):
  id = models.CharField('id', max_length=50, primary_key=True)
  name = models.CharField(max_length=50)
  tel = models.IntegerField()
  address = models.CharField(max_length=50)
  allowance = models.FloatField(max_length=50, default=1)
  def __str__(self):
    return f'{self.pk}) {self.name}'
  
class PositionList(models.Model):
  id = models.CharField('id', max_length=50, primary_key=True)
  name = models.CharField(max_length=50)
  salaryOfTime = models.IntegerField()
  timeWorkByDay = models.IntegerField(default='8')
  def __str__(self):
    return f'{self.pk}) {self.name}'
  
