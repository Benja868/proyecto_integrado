from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.usuarios_list, name='list'),
    path('nuevo/', views.usuarios_create, name='create'),
    path('editar/<int:pk>/', views.usuarios_update, name='update'),
    path('eliminar/<int:pk>/', views.usuarios_delete, name='delete'),
]
