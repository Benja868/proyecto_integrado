# dulceria_lilis/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler403
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),                   # Home, dashboard, etc.
    path('catalogo/', include('catalogo.urls')),      # Catálogo público
    path('empresa/', include('empresa.urls')),        # Nosotros
    path('accounts/', include('accounts.urls')),      # Login, logout, registro
    path('proveedores/', include('proveedores.urls')), # CRUD proveedores
    path('inventario/', include('inventario.urls')),   # Módulo de inventario
    path('usuarios/', include('usuarios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

def error_403(request, exception=None):
    return render(request, '403.html', status=403)

def error_404(request, exception=None):
    return render(request, '404.html', status=404)

handler403 = 'dulceria_lilis.urls.error_403'
handler404 = 'dulceria_lilis.urls.error_404'