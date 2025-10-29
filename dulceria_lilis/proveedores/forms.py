# proveedores/forms.py
from django import forms
from .models import Supplier

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__' # O listar campos explícitamente
        widgets = {
            'razon_social': forms.TextInput(attrs={'placeholder': 'Nombre legal completo'}),
            'rut_nif': forms.TextInput(attrs={'placeholder': 'Ej: 76543210-5'}),
            'email': forms.EmailInput(attrs={'placeholder': 'correo@proveedor.com'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'pais': forms.TextInput(attrs={'readonly': 'readonly'}), # Default Chile, no editable
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_rut_nif(self):
        # Aquí puedes añadir validación del formato RUT chileno si lo necesitas
        rut = self.cleaned_data.get('rut_nif')
        # ... lógica de validación ...
        return rut