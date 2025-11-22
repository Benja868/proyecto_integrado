# inventario/urls.py
from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.movement_list, name='list'),
    path('nuevo/', views.movement_create, name='create'),
    path('stock/', views.stock_list, name='stock_list'),
    path('exportar/', views.exportar_inventario_excel, name='exportar_inventario_excel'),
]