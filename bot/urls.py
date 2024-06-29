from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('getpost/', views.telegram_bot, name='telegram_bot'),
    path('setwebhook/', views.setwebhook, name='setwebhook')
]