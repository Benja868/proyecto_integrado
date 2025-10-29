# core/forms.py
from django import forms
from .models import Compra, Venta, Produccion, Finanzas

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['producto', 'proveedor', 'cantidad', 'total', 'fecha_compra', 'doc_referencia']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_compra': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'doc_referencia': forms.TextInput(attrs={'class': 'form-control'}),
        }

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['producto', 'cantidad', 'total', 'fecha_venta', 'doc_referencia']  # ✅ cliente eliminado
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_venta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'doc_referencia': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProduccionForm(forms.ModelForm):
    class Meta:
        model = Produccion
        fields = ['producto', 'cantidad_producida', 'fecha_produccion']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_producida': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'fecha_produccion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

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
