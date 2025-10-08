from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # precio
    stock = models.PositiveIntegerField(default=0)  # cantidad
    available = models.BooleanField(default=True)  # disponible o no

    def __str__(self):
        return f"{self.name} ({self.sku})"

class AlertRule(models.Model):  
    SEVERITY_CHOICES = [
        ("Low", "Baja"),
        ("Medium", "Media"),
        ("High", "Alta"),
    ]
    name = models.CharField(max_length=100)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)

    def __str__(self):
        return f"{self.name} [{self.severity}]"


class ProductAlertRule(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE)
    min_value = models.IntegerField()
    max_value = models.IntegerField()

    class Meta:
        unique_together = ("product", "alert_rule")

    def __str__(self):
        return f"{self.product.name} - {self.alert_rule.name}"
