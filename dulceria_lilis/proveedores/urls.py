# proveedores/urls.py
from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    path('', views.proveedores_list, name='list'),
    path('nuevo/', views.proveedor_create, name='create'),
    path('editar/<int:pk>/', views.proveedor_update, name='update'),
    # path('eliminar/<int:pk>/', views.proveedor_delete, name='delete'), # Descomentar si creas la vista
]