from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Página de inicio
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard
]
