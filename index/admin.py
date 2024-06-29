from django.contrib import admin
from index.models import *
from django.apps import apps

for model in apps.get_app_config('index').models.values():
    admin.site.register(model)