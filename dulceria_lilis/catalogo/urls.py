from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalogo_principal, name='catalogo_principal'),  # Esta línea es crucial
    path('<str:categoria>/', views.subcatalogo, name='subcatalogo'),
    path('<str:categoria>/<str:producto_id>/', views.detalle_producto, name='detalle_producto'),
]