from django.urls import path
from . import views
from . import views_perfil

app_name = 'usuarios'

urlpatterns = [
    path('', views.usuarios_list, name='list'),
    path('nuevo/', views.usuario_create, name='create'),
    path('editar/<int:pk>/', views.usuario_update, name='update'),
    path('eliminar/<int:pk>/', views.usuario_delete, name='delete'),
    path('perfil/', views_perfil.perfil_usuario, name='perfil'),
    path('cambiar-contrasena/', views_perfil.cambiar_contrasena, name='cambiar_contrasena'),
]
