from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [

    # --- URLs para Gestión de Productos ---
    path('gestion/productos/', views.ProductListView.as_view(), name='product_list'),
    path('gestion/productos/nuevo/', views.ProductCreateView.as_view(), name='product_create'),
    path('gestion/productos/editar/<int:pk>/', views.ProductUpdateView.as_view(), name='product_update'),
    path('gestion/productos/eliminar/<int:pk>/', views.ProductDeleteView.as_view(), name='product_delete'),

    # --- EXPORTACIONES (💥 deben ir antes de rutas con variables) ---
    path('productos/exportar/', views.exportar_productos_excel, name='exportar_productos_excel'),
    path('categorias/exportar/', views.exportar_categorias_excel, name='exportar_categorias_excel'),

    # --- Catálogo Público ---
    path('', views.catalogo_principal, name='catalogo_principal'),
    path('<str:categoria_slug>/', views.subcatalogo, name='subcatalogo'),
    path('<str:categoria_slug>/<str:producto_slug>/', views.detalle_producto, name='detalle_producto'),
]
