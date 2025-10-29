# catalogo/models.py
from django.db import models
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # Podrías añadir campos como 'description' si es útil

    def __str__(self):
        return self.name

class Brand(models.Model): # Modelo para Marca (PDF Opcional)
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class UnitOfMeasure(models.Model): # Modelo para Unidades de Medida
    code = models.CharField(max_length=10, unique=True, help_text="Ej: UN, CAJA, KG") # PDF Requerido
    name = models.CharField(max_length=50) # Nombre descriptivo, ej: Unidad, Caja x 12, Kilogramo
    def __str__(self): return f"{self.name} ({self.code})"

class Product(models.Model):
    # --- Identificación (PDF) ---
    sku = models.CharField(max_length=50, unique=True) # Requerido
    ean_upc = models.CharField(max_length=50, unique=True, null=True, blank=True) # Opcional
    name = models.CharField(max_length=150) # Requerido
    description = models.TextField(blank=True) # Opcional
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products") # Requerido
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True) # Opcional
    model_name = models.CharField(max_length=100, blank=True, verbose_name="Modelo") # Opcional (PDF)

    # --- Unidades y Precios (PDF) ---
    uom_purchase = models.ForeignKey(UnitOfMeasure, related_name='products_purchase', on_delete=models.PROTECT, verbose_name="UdM Compra") # Requerido
    uom_sale = models.ForeignKey(UnitOfMeasure, related_name='products_sale', on_delete=models.PROTECT, verbose_name="UdM Venta") # Requerido
    conversion_factor = models.DecimalField(max_digits=12, decimal_places=6, default=1.0, verbose_name="Factor Conversión") # Requerido PDF (Compra -> Venta)
    standard_cost = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True, verbose_name="Costo Estándar") # Opcional
    # average_cost: Se calculará/actualizará desde inventario (solo lectura aquí)
    sale_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True, verbose_name="Precio Venta Base") # Opcional (Precio base sin IVA)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=19.0, verbose_name="Tasa IVA (%)") # Requerido PDF

    # --- Stock y Control (PDF) ---
    stock_min = models.DecimalField(max_digits=18, decimal_places=4, default=0, verbose_name="Stock Mínimo") # Requerido
    stock_max = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True, verbose_name="Stock Máximo") # Opcional
    reorder_point = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True, verbose_name="Punto Reorden") # Opcional
    is_perishable = models.BooleanField(default=False, verbose_name="Perecible") # Requerido
    lot_controlled = models.BooleanField(default=False, verbose_name="Control por Lote") # Requerido
    serial_controlled = models.BooleanField(default=False, verbose_name="Control por Serie") # Requerido

    # --- Relaciones y Soporte (PDF) ---
    image_url = models.URLField(max_length=255, blank=True, verbose_name="URL Imagen") # Opcional
    datasheet_url = models.URLField(max_length=255, blank=True, verbose_name="URL Ficha Técnica") # Opcional

    # --- Otros campos ---
    available = models.BooleanField(default=True, verbose_name="Disponible para venta") # Mantenido, podría derivarse del stock

    # --- Campos derivados (implementar lógica en vistas/managers) ---
    # stock_actual (se calculará desde inventario)
    # alerta_bajo_stock (se calculará)
    # alerta_por_vencer (se calculará desde inventario)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def clean(self):
        if self.conversion_factor <= 0:
            raise ValidationError({'conversion_factor': "El factor de conversión debe ser positivo."})
        if self.serial_controlled and self.lot_controlled:
            # Podría permitirse, pero usualmente es uno u otro. Aclarar requerimiento.
            pass
        # Añadir más validaciones si es necesario

    # Podrías añadir propiedades @property para calcular precios con IVA, etc.


# AlertRule y ProductAlertRule se mantienen como estaban para las alertas de stock bajo/crítico.
class AlertRule(models.Model):
    SEVERITY_CHOICES = [("Low", "Baja"), ("Medium", "Media"), ("High", "Alta")]
    name = models.CharField(max_length=100)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    def __str__(self): return f"{self.name} [{self.severity}]"

class ProductAlertRule(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE)
    min_value = models.DecimalField(max_digits=18, decimal_places=4) # Ajustado a Decimal
    max_value = models.DecimalField(max_digits=18, decimal_places=4) # Ajustado a Decimal
    # Asegúrate que min/max se refieran a la uom_sale del producto

    class Meta:
        unique_together = ("product", "alert_rule")
    def __str__(self): return f"{self.product.name} - {self.alert_rule.name}"