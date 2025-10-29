# dulceria_lilis/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),                   # Home, dashboard, etc.
    path('catalogo/', include('catalogo.urls')),      # Catálogo público
    path('empresa/', include('empresa.urls')),        # Nosotros
    path('accounts/', include('accounts.url')),      # Login, logout, registro
    path('proveedores/', include('proveedores.urls')), # CRUD proveedores
    path('inventario/', include('inventario.urls')),   # Módulo de inventario
    path('usuarios/', include('usuarios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
