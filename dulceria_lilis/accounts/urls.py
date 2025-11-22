from django.urls import path
from .views import login_view, register, profile, password_reset_request, password_reset_code, password_reset_confirm
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),

    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset/code/', password_reset_code, name='password_reset_code'),
    path('password-reset/confirm/', password_reset_confirm, name='password_reset_confirm'),
]
