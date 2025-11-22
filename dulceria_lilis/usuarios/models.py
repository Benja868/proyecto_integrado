from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils import timezone
from datetime import timedelta
class Usuario(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True, null=True)
    intentos_fallidos = models.IntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(blank=True, null=True)

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

    # 🔥 NUEVO: marca si el usuario debe cambiar la contraseña al iniciar sesión
    password_must_change = models.BooleanField(default=False)

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

    def esta_bloqueado(self):
        """Retorna True si el usuario está bloqueado temporalmente."""
        if self.bloqueado_hasta and self.bloqueado_hasta > timezone.now():
            return True
        return False

    def bloquear(self, minutos=15):
        """Bloquea al usuario por X minutos."""
        self.bloqueado_hasta = timezone.now() + timedelta(minutes=minutos)
        self.save()

    def resetear_intentos(self):
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        self.save()
