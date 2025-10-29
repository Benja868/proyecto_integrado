# inventario/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError # <<< IMPORTACIÓN AÑADIDA

# Nota: Asegúrate que las apps 'catalogo' y 'proveedores' estén antes que 'inventario'
# en INSTALLED_APPS si usas nombres de string como 'catalogo.Product'.
# Alternativamente, importa directamente los modelos al inicio del archivo.
# from catalogo.models import Product, UnitOfMeasure
# from proveedores.models import Supplier

class Warehouse(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre Bodega")
    location = models.CharField(max_length=200, blank=True, verbose_name="Ubicación")

    def __str__(self): return self.name

class InventoryMovementType(models.Model):
    # Ejemplos: INGRESO_COMPRA, SALIDA_VENTA, AJUSTE_POSITIVO, AJUSTE_NEGATIVO,
    # TRANSFERENCIA_SALIDA, TRANSFERENCIA_ENTRADA, DEVOLUCION_CLIENTE, DEVOLUCION_PROVEEDOR, INGRESO_PRODUCCION
    code = models.CharField(max_length=30, unique=True, verbose_name="Código Tipo Mov.")
    name = models.CharField(max_length=100, verbose_name="Nombre Tipo Mov.")
    is_entry = models.BooleanField(verbose_name="Es Entrada (+)", help_text="Marca si suma al stock, desmarca si resta.")

    def __str__(self): return self.name

class InventoryMovement(models.Model):
    movement_type = models.ForeignKey(InventoryMovementType, on_delete=models.PROTECT, verbose_name="Tipo Movimiento")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora")
    product = models.ForeignKey('catalogo.Product', on_delete=models.PROTECT, verbose_name="Producto")
    quantity = models.DecimalField(max_digits=18, decimal_places=4, verbose_name="Cantidad")
    uom = models.ForeignKey('catalogo.UnitOfMeasure', on_delete=models.PROTECT, verbose_name="UdM")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="Bodega")
    unit_cost = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True, verbose_name="Costo Unitario")

    # --- Control Avanzado (PDF) ---
    lot_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Lote")
    serial_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Serie")
    expiry_date = models.DateField(blank=True, null=True, verbose_name="Fecha Vencimiento")

    # --- Referencias (PDF) ---
    doc_reference = models.CharField(max_length=100, blank=True, verbose_name="Doc. Referencia", help_text="Ej: OC-123, FAC-456, GUIA-789")
    reason = models.CharField(max_length=200, blank=True, verbose_name="Motivo (Ajuste/Dev.)")
    observations = models.TextField(blank=True, verbose_name="Observaciones")
    supplier = models.ForeignKey('proveedores.Supplier', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proveedor")
    # cliente = models.ForeignKey('core.Cliente', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cliente") # Si aplica

    # --- Auditoría ---
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='inventory_movements_created', verbose_name="Creado por")

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        sign = "+" if self.movement_type.is_entry else "-"
        # Format timestamp safely using Django template filters logic if needed, basic format here
        ts_formatted = self.timestamp.strftime('%Y-%m-%d %H:%M') if self.timestamp else 'N/A'
        return f"{ts_formatted} | {self.movement_type.code} | {self.product.sku} | {sign}{self.quantity} {self.uom.code} @ {self.warehouse.name}"

    def clean(self):
        # Validaciones del modelo antes de guardar
        if self.product.lot_controlled and not self.lot_number:
            raise ValidationError({'lot_number': 'Se requiere lote para este producto.'}) # Corregido
        if self.product.serial_controlled and not self.serial_number:
            raise ValidationError({'serial_number': 'Se requiere serie para este producto.'}) # Corregido
        if self.product.is_perishable and not self.expiry_date:
            # Considerar si la fecha de vencimiento es obligatoria en todos los casos para perecibles
            # Podría ser opcional dependiendo del tipo de movimiento (ej. ajuste negativo no necesita fecha)
            # if self.movement_type and self.movement_type.is_entry: # Ejemplo: Requerir solo en entradas
            #     raise ValidationError({'expiry_date': 'Se requiere fecha de vencimiento para entradas de este producto perecible.'})
            pass # Por ahora se permite nulo
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'La cantidad debe ser positiva.'}) # Corregido


# Modelo opcional para consulta rápida de stock (denormalizado)
class InventoryStock(models.Model):
    product = models.ForeignKey('catalogo.Product', on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=18, decimal_places=4, default=0, verbose_name="Cantidad Actual")
    # average_cost = models.DecimalField(max_digits=18, decimal_places=6, default=0)

    last_updated = models.DateTimeField(auto_now=True)

class Meta:
    unique_together = ('product', 'warehouse')
    verbose_name = "Stock Actual"
    verbose_name_plural = "Stocks Actuales"

    def __str__(self):
        return f"{self.product.sku} @ {self.warehouse.name}: {self.quantity}"
