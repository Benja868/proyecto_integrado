from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Zone(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="zones")

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Device(models.Model):
    name = models.CharField(max_length=150)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="devices")
    serial = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name} ({self.serial})"


class Measurement(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="measurements")
    value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.name} - {self.value} ({self.created_at})"
