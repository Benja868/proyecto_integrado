# proveedores/models.py
from django.db import models

class Supplier(models.Model):
    STATUS_CHOICES = (('ACTIVO', 'Activo'), ('BLOQUEADO', 'Bloqueado'))
    rut_nif = models.CharField(max_length=20, unique=True) # Requerido PDF
    razon_social = models.CharField(max_length=255) # Requerido PDF
    nombre_fantasia = models.CharField(max_length=255, blank=True) # Opcional PDF
    email = models.EmailField(max_length=254) # Requerido PDF (ajustado de unique=True)
    telefono = models.CharField(max_length=30, blank=True) # Opcional PDF
    sitio_web = models.URLField(max_length=255, blank=True) # Opcional PDF
    direccion = models.CharField(max_length=255, blank=True) # Opcional PDF
    ciudad = models.CharField(max_length=128, blank=True) # Opcional PDF
    pais = models.CharField(max_length=64, default="Chile") # Requerido PDF
    condiciones_pago = models.CharField(max_length=100) # Requerido PDF
    moneda = models.CharField(max_length=8, default='CLP') # Requerido PDF
    contacto_principal_nombre = models.CharField(max_length=120, blank=True) # Opcional PDF
    contacto_principal_email = models.EmailField(max_length=254, blank=True) # Opcional PDF
    contacto_principal_telefono = models.CharField(max_length=30, blank=True) # Opcional PDF
    estado = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVO') # Requerido PDF
    observaciones = models.TextField(blank=True) # Opcional PDF
    # fecha_registro = models.DateField(auto_now_add=True) # Opcional, mantener si es útil

    def __str__(self):
        return self.razon_social

# Crear también el modelo ProductSupplier aquí si no lo has hecho
class ProductSupplier(models.Model):
    product = models.ForeignKey('catalogo.Product', on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=18, decimal_places=6)
    lead_time_days = models.IntegerField(default=7)
    min_batch = models.DecimalField(max_digits=18, decimal_places=6, default=1)
    discount_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_preferred = models.BooleanField(default=False)

    class Meta:
        unique_together = ('product', 'supplier')

    def __str__(self):
        return f"{self.product.name} - {self.supplier.razon_social}"