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

    # Exportación a Excel
    path("compras/exportar-excel/", views.exportar_compras_excel, name="compras_export"),
    path("produccion/exportar-excel/", views.exportar_produccion_excel, name="produccion_export"),
    path("ventas/exportar-excel/", views.exportar_ventas_excel, name="ventas_export"),
    path("finanzas/exportar-excel/", views.exportar_finanzas_excel, name="finanzas_export"),


    # 🧹 Usuarios y Proveedores ahora se gestionan desde sus propias apps:
    #   usuarios/urls.py   → gestión de usuarios
    #   proveedores/urls.py → gestión de proveedores
]
