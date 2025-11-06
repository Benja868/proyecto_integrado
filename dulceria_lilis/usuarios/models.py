from django.contrib.auth.models import AbstractUser, Group
from django.db import models

class Usuario(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True, null=True)

    ROLES = [
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('operador', 'Operador'),
    ]
    rol = models.CharField(
        max_length=30,
        choices=ROLES,
        default='operador'
    )

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    estado = models.BooleanField(default=True)
    mfa_habilitado = models.BooleanField(default=False)
    ultimo_acceso = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

    def save(self, *args, **kwargs):
        """Sincroniza automáticamente el rol con los grupos de Django"""
        super().save(*args, **kwargs)

        # Elimina grupos anteriores para evitar duplicidad
        self.groups.clear()

        # Asigna el grupo según el rol
        if self.rol == 'admin':
            group, _ = Group.objects.get_or_create(name='Administrador')
        elif self.rol == 'supervisor':
            group, _ = Group.objects.get_or_create(name='Supervisor')
        else:
            group, _ = Group.objects.get_or_create(name='Operador')

        self.groups.add(group)
