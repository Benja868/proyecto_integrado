from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario

class UsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'telefono', 'rol', 'estado', 'mfa_habilitado'
        ]
        widgets = {
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mfa_habilitado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UsuarioEditForm(UserChangeForm):
    password = None  # Ocultamos el campo contraseña
    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'telefono', 'rol', 'estado', 'mfa_habilitado'
        ]
