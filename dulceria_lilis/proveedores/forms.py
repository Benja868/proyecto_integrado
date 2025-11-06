# proveedores/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import Supplier
import re

class SupplierForm(forms.ModelForm):
    rut_nif = forms.CharField(
        label="RUT / NIF",
        validators=[
            RegexValidator(
                r'^[0-9]+[-|‐]{1}[0-9kK]{1}$',
                'El RUT/NIF debe tener el formato correcto (Ej: 12345678-9).'
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 12345678-9'})
    )

    telefono = forms.CharField(
        label="Teléfono",
        required=True,
        validators=[
            RegexValidator(
                r'^\+?\d{8,15}$',
                'El teléfono debe contener entre 8 y 15 dígitos y puede incluir prefijo (+56).'
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': '+56912345678'})
    )

    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'correo@proveedor.com'})
    )

    class Meta:
        model = Supplier
        fields = '__all__'
        widgets = {
            'razon_social': forms.TextInput(attrs={'placeholder': 'Nombre legal completo'}),
            'nombre_fantasia': forms.TextInput(attrs={'placeholder': 'Nombre comercial'}),
            'contacto_principal_nombre': forms.TextInput(attrs={'placeholder': 'Nombre del contacto principal'}),
            'contacto_principal_email': forms.EmailInput(attrs={'placeholder': 'correo@empresa.com'}),
            'contacto_principal_telefono': forms.TextInput(attrs={'placeholder': '+56999999999'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Dirección completa'}),
            'ciudad': forms.TextInput(attrs={'placeholder': 'Ciudad'}),
            'pais': forms.TextInput(attrs={'readonly': 'readonly'}),  # Chile por defecto
            'condiciones_pago': forms.TextInput(attrs={'placeholder': 'Ej: 30 días'}),
            'moneda': forms.TextInput(attrs={'placeholder': 'Ej: CLP'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Notas adicionales...'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    # --- VALIDACIONES PERSONALIZADAS ---

    def clean_rut_nif(self):
        rut = self.cleaned_data.get('rut_nif')
        if rut:
            rut = rut.replace(".", "").replace("-", "").upper()
            cuerpo, dv = rut[:-1], rut[-1]

            if not cuerpo.isdigit():
                raise ValidationError("El RUT contiene caracteres no válidos.")

            suma = 0
            multiplo = 2
            for c in reversed(cuerpo):
                suma += int(c) * multiplo
                multiplo = 9 if multiplo == 7 else multiplo + 1

            resto = suma % 11
            dv_esperado = "K" if resto == 1 else "0" if resto == 0 else str(11 - resto)
            if dv_esperado != dv:
                raise ValidationError("El RUT ingresado no es válido.")
        return rut

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise ValidationError("El correo electrónico no tiene un formato válido.")

        # Verificar duplicado
        proveedor_id = self.instance.id if self.instance else None
        if Supplier.objects.exclude(id=proveedor_id).filter(email=email).exists():
            raise ValidationError("Este correo ya está registrado para otro proveedor.")
        return email

    def clean_contacto_principal_email(self):
        email = self.cleaned_data.get('contacto_principal_email')
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise ValidationError("El correo del contacto principal no es válido.")
        return email

    def clean_contacto_principal_telefono(self):
        telefono = self.cleaned_data.get('contacto_principal_telefono')
        if telefono and not re.match(r'^\+?\d{8,15}$', telefono):
            raise ValidationError("El teléfono del contacto debe ser numérico (ej: +56912345678).")
        return telefono

    def clean_razon_social(self):
        razon_social = self.cleaned_data.get('razon_social')
        proveedor_id = self.instance.id if self.instance else None
        if Supplier.objects.exclude(id=proveedor_id).filter(razon_social__iexact=razon_social).exists():
            raise ValidationError("Ya existe un proveedor con esta razón social.")
        return razon_social
