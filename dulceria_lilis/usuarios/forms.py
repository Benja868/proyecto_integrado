from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import Usuario
import re

class UsuarioForm(UserCreationForm):
    telefono = forms.CharField(
        required=True,
        validators=[
            RegexValidator(
                r'^\+?\d{8,15}$',
                'El número de teléfono debe contener solo dígitos y puede incluir el prefijo internacional (+56...).'
            )
        ]
    )

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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('Este correo ya está registrado.')
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise ValidationError('Correo electrónico inválido.')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")

        # Reglas de contraseña segura
        if len(password1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Z]", password1):
            raise ValidationError("Debe incluir al menos una letra mayúscula.")
        if not re.search(r"\d", password1):
            raise ValidationError("Debe incluir al menos un número.")
        if not re.search(r"[@$!%*?&]", password1):
            raise ValidationError("Debe incluir al menos un símbolo especial (@, $, !, %, *, ?, &).")

        return password2


class UsuarioEditForm(UserChangeForm):
    password = None  # Oculta el campo contraseña

    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'telefono', 'rol', 'estado', 'mfa_habilitado'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.id
        if Usuario.objects.exclude(id=user_id).filter(email=email).exists():
            raise ValidationError('Este correo ya está en uso por otro usuario.')
        return email
