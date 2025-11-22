# core/forms.py
from django import forms

from catalogo.models import Product       # 👈 IMPORTA EL MODELO CORRECTO
from proveedores.models import Supplier # 👈 El proveedor real
from .models import Compra, Venta, Produccion, Finanzas


# ===========================================================
#   FORMULARIO DE COMPRAS
# ===========================================================
class CompraForm(forms.ModelForm):

    producto = forms.ModelChoiceField(
        queryset=Product.objects.filter(available=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Producto"
    )

    proveedor = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Proveedor"
    )

    class Meta:
        model = Compra
        fields = ['producto', 'proveedor', 'cantidad', 'total', 'fecha_compra', 'doc_referencia']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_compra': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'doc_referencia': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ===========================================================
#   FORMULARIO DE VENTAS
# ===========================================================
class VentaForm(forms.ModelForm):

    producto = forms.ModelChoiceField(
        queryset=Product.objects.filter(available=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Producto"
    )

    class Meta:
        model = Venta
        fields = ['producto', 'cantidad', 'total', 'fecha_venta', 'doc_referencia']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_venta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'doc_referencia': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ===========================================================
#   FORMULARIO DE PRODUCCIÓN
# ===========================================================
class ProduccionForm(forms.ModelForm):

    producto = forms.ModelChoiceField(
        queryset=Product.objects.filter(available=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Producto"
    )

    class Meta:
        model = Produccion
        fields = ['producto', 'cantidad_producida', 'fecha_produccion']
        widgets = {
            'cantidad_producida': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'fecha_produccion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


# ===========================================================
#   FORMULARIO DE FINANZAS
# ===========================================================
class FinanzasForm(forms.ModelForm):
    class Meta:
        model = Finanzas
        fields = ['descripcion', 'ingreso', 'gasto', 'fecha']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
            'ingreso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'gasto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
