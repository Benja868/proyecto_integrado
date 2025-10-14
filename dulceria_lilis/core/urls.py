from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Página de inicio
    path('dashboard/', views.dashboard, name='dashboard'),
    path('inventario/', views.inventario, name='inventario'),
    path('compras/', views.compras, name='compras'),
    path('produccion/', views.produccion, name='produccion'),
    path('ventas/', views.ventas, name='ventas'),
    path('finanzas/', views.finanzas, name='finanzas'),
    path('clientes/', views.clientes, name='clientes'),
]  

