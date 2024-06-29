from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.views.decorators.csrf import csrf_exempt
from index.views import WorkerApiView, PositionListApiView, BuildObjectApiView, ClientsApiView, salary
from index.scripts.overTimeCheck import overTimeCheck
import bot.urls


router = routers.DefaultRouter()
router.register(r'api/worker', WorkerApiView, basename='generalWorker')
router.register(r'api/position-list', PositionListApiView)
router.register(r'api/build-object', BuildObjectApiView)
router.register(r'api/client', ClientsApiView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('over-time-check/', overTimeCheck),
    path('salary/', salary),
    path('', include(bot.urls)),
    path('', include(router.urls)),
]



