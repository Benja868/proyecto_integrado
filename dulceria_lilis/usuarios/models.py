from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True, null=True)
    rol = models.CharField(
        max_length=30,
        choices=[
            ('admin', 'Administrador'),
            ('operador', 'Operador'),
            ('vendedor', 'Vendedor'),
        ],
        default='operador'
    )
    estado = models.BooleanField(default=True)
    mfa_habilitado = models.BooleanField(default=False)
    ultimo_acceso = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
