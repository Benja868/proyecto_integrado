from django.urls import path
from . import views

app_name = "proveedores"

urlpatterns = [
    path("", views.proveedores_list, name="list"),
    path("nuevo/", views.proveedor_create, name="create"),
    path("<int:pk>/editar/", views.proveedor_update, name="update"),
    path("<int:pk>/eliminar/", views.proveedor_delete, name="delete"),
    path("exportar_excel/", views.exportar_proveedores_excel, name="exportar_excel"),
]
