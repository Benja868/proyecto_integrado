from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import Usuario


# =============================
# VALIDADORES PERSONALIZADOS
# =============================

solo_letras_regex = RegexValidator(
    regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$',
    message="Solo se permiten letras y espacios."
)

telefono_regex = RegexValidator(
    regex=r'^\+?\d{8,15}$',
    message="El teléfono debe contener solo números y opcionalmente un '+' al inicio."
)


# =============================
# FORMULARIO PERFIL
# =============================

class PerfilForm(forms.ModelForm):

    first_name = forms.CharField(
        max_length=30,
        validators=[solo_letras_regex],
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        max_length=30,
        validators=[solo_letras_regex],
        label="Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    telefono = forms.CharField(
        validators=[telefono_regex],
        label="Teléfono",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'avatar']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

    # Validación completa del formulario
    def clean(self):
        cleaned_data = super().clean()

        telefono = cleaned_data.get("telefono")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")

        # Validar teléfono manualmente para mostrar errores más claros
        if telefono and not telefono_regex.regex.match(telefono):
            self.add_error(
                "telefono",
                "Formato inválido. Ejemplos válidos: +56912345678, 912345678"
            )

        # Validación adicional de nombres sin números
        if first_name and any(char.isdigit() for char in first_name):
            self.add_error("first_name", "El nombre no puede contener números.")

        if last_name and any(char.isdigit() for char in last_name):
            self.add_error("last_name", "El apellido no puede contener números.")

        return cleaned_data


# =============================
# CAMBIO DE CONTRASEÑA
# =============================
class CustomPasswordChangeForm(PasswordChangeForm):

    old_password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña actual'
        })
    )

    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña segura'
        })
    )

    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite la nueva contraseña'
        })
    )
