# core/forms.py
from django import forms
from .models import Cliente, Producto, Compra, Venta, Produccion, Finanzas

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'email', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
        }

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'stock', 'precio']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Categoría'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['producto', 'cantidad', 'total']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['producto', 'cantidad', 'total']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class ProduccionForm(forms.ModelForm):
    class Meta:
        model = Produccion
        fields = ['producto', 'cantidad_producida']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_producida': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class FinanzasForm(forms.ModelForm):
    class Meta:
        model = Finanzas
        fields = ['descripcion', 'ingreso', 'gasto']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
            'ingreso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'gasto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
