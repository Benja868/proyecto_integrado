# core/models.py
from django.db import models
from django.utils import timezone
from proveedores.models import Supplier


# --------------------------------------------------------------------
# PRODUCTO (referencia interna mínima)
# --------------------------------------------------------------------
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)  # puede reemplazarse por ForeignKey a Category
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Base Venta")

    def __str__(self):
        return self.nombre


# --------------------------------------------------------------------
# COMPRA
# --------------------------------------------------------------------
class Compra(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_compra = models.DateField(default=timezone.now)
    doc_referencia = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Compra #{self.id} - {self.producto.nombre} ({self.proveedor.razon_social})"


# --------------------------------------------------------------------
# VENTA
# --------------------------------------------------------------------
class Venta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_venta = models.DateField(default=timezone.now)
    doc_referencia = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Venta #{self.id} - {self.producto.nombre}"


# --------------------------------------------------------------------
# PRODUCCIÓN
# --------------------------------------------------------------------
class Produccion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_producida = models.PositiveIntegerField()
    fecha_produccion = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Producción {self.producto.nombre} ({self.cantidad_producida})"


# --------------------------------------------------------------------
# FINANZAS
# --------------------------------------------------------------------
class Finanzas(models.Model):
    descripcion = models.CharField(max_length=200)
    ingreso = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gasto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.descripcion} - {self.fecha}"
