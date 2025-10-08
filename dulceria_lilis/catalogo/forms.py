from django import forms
from django.core.exceptions import ValidationError
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

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
