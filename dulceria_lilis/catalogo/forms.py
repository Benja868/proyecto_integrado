# catalogo/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category, Brand, UnitOfMeasure # Importar todos los modelos necesarios

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # fields = "__all__" # O listar explícitamente los campos editables
        exclude = [] # Excluir campos calculados o gestionados por otros módulos

        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'sku': forms.TextInput(attrs={'placeholder': 'SKU único'}),
            'ean_upc': forms.TextInput(attrs={'placeholder': 'Código de barras (opcional)'}),
            'name': forms.TextInput(attrs={'placeholder': 'Nombre descriptivo del producto'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'uom_purchase': forms.Select(attrs={'class': 'form-select'}),
            'uom_sale': forms.Select(attrs={'class': 'form-select'}),
            'conversion_factor': forms.NumberInput(attrs={'step': '0.0001'}),
            'standard_cost': forms.NumberInput(attrs={'step': '0.000001'}),
            'sale_price': forms.NumberInput(attrs={'step': '0.01'}),
            'tax_rate': forms.NumberInput(attrs={'step': '0.01'}),
            'stock_min': forms.NumberInput(attrs={'step': '0.0001'}),
            'stock_max': forms.NumberInput(attrs={'step': '0.0001'}),
            'reorder_point': forms.NumberInput(attrs={'step': '0.0001'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'datasheet_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }

    # Mantener las validaciones clean_price (ahora clean_sale_price) y clean_stock
    # si esos campos aún existen y tienen lógica específica.
    # Por ahora, las eliminaremos ya que 'stock' se gestionará en inventario
    # y 'sale_price' no tiene la validación de negativo (puede ser 0).

    def clean_conversion_factor(self):
        factor = self.cleaned_data.get("conversion_factor")
        if factor is not None and factor <= 0:
            raise ValidationError("El factor de conversión debe ser positivo.")
        return factor

    # Añadir más validaciones si es necesario

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise ValidationError("El precio no puede ser negativo.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock > 1000:
            raise ValidationError("El stock no puede superar 1000 unidades.")
        return stock
