# inventario/forms.py
from django import forms
from .models import InventoryMovement, Warehouse, InventoryMovementType
from catalogo.models import Product, UnitOfMeasure

class InventoryMovementForm(forms.ModelForm):

    class Meta:
        model = InventoryMovement
        exclude = ['created_by'] # Se asignará en la vista
        widgets = {
            'timestamp': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'movement_type': forms.Select(attrs={'class': 'form-select'}),
            'product': forms.Select(attrs={'class': 'form-select'}), # Podría necesitar Select2 para buscar
            'quantity': forms.NumberInput(attrs={'step': '0.0001'}),
            'uom': forms.Select(attrs={'class': 'form-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'unit_cost': forms.NumberInput(attrs={'step': '0.000001'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'observations': forms.Textarea(attrs={'rows': 3}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Podrías filtrar UOM basado en el producto seleccionado usando JS o htmx
        # Opcional: Ocultar/mostrar campos lote/serie/vencimiento según el producto
        # if self.instance and self.instance.pk: # Si es edición
        #    product = self.instance.product
        # else: # Si es creación (o podrías pasar producto inicial)
        #     try: product = Product.objects.get(pk=self.initial.get('product'))
        #     except: product = None

        # if not (product and product.lot_controlled):
        #     self.fields['lot_number'].widget = forms.HiddenInput()
        # if not (product and product.serial_controlled):
        #     self.fields['serial_number'].widget = forms.HiddenInput()
        # if not (product and product.is_perishable):
        #     self.fields['expiry_date'].widget = forms.HiddenInput()


    # Añadir validaciones clean_quantity, clean_lot_number, etc. si es necesario
    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty is not None and qty <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor que cero.")
        return qty

    # Añadir clean() para validar lote/serie/vencimiento según el producto seleccionado
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        lot = cleaned_data.get('lot_number')
        serial = cleaned_data.get('serial_number')
        expiry = cleaned_data.get('expiry_date')
        mvt_type = cleaned_data.get('movement_type')

        if product:
            if product.lot_controlled and not lot:
                self.add_error('lot_number', 'Se requiere lote para este producto.')
            if product.serial_controlled and not serial:
                self.add_error('serial_number', 'Se requiere serie para este producto.')
            # Validar vencimiento solo si es perecible y es un movimiento de entrada?
            if product.is_perishable and not expiry and mvt_type and mvt_type.is_entry:
                self.add_error('expiry_date', 'Se requiere fecha de vencimiento para este producto perecible.')
        return cleaned_data