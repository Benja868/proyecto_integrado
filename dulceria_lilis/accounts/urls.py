# accounts/urls.py
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Login y Logout
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page=reverse_lazy('login')),  # redirige al login tras cerrar sesión
        name='logout'
    ),

    # Registro y Perfil
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),

    # Recuperar contraseña personalizada
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/code/', views.password_reset_code, name='password_reset_code'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
]
