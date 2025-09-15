from django.urls import path
from . import views

urlpatterns = [
    path('', views.informacion_empresa, name='informacion_empresa'),
]