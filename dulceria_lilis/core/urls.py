# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Página principal
    path('', views.home, name='home'),

    # Panel principal
    path('dashboard/', views.dashboard, name='dashboard'),

    # Secciones del panel
    path('compras/', views.compras, name='compras'),
    path('produccion/', views.produccion, name='produccion'),
    path('ventas/', views.ventas, name='ventas'),
    path('finanzas/', views.finanzas, name='finanzas'),

    # 🧹 Usuarios y Proveedores ahora se gestionan desde sus propias apps:
    #   usuarios/urls.py   → gestión de usuarios
    #   proveedores/urls.py → gestión de proveedores
]
