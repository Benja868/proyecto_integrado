from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=191, unique=True)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=191, unique=True)
    direccion = models.CharField(max_length=200)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    stock = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre


class Compra(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_compra = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Compra #{self.id} - {self.producto.nombre}"


class Venta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Venta #{self.id} - {self.producto.nombre}"


class Produccion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_producida = models.PositiveIntegerField()
    fecha_produccion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad_producida}"


class Finanzas(models.Model):
    descripcion = models.CharField(max_length=200)
    ingreso = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gasto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.descripcion} ({self.fecha})"
