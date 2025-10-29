# accounts/models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group, User

# Organization, Module, Role, RoleModulePermission se mantienen como estaban.

class Organization(models.Model):
    name = models.CharField(max_length=150, unique=True)
    def __str__(self): return self.name

class UserProfile(models.Model):
    STATUS_CHOICES = (
        ('ACTIVO', 'Activo'),
        ('BLOQUEADO', 'Bloqueado'),
        # Puedes añadir INACTIVO si es necesario
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='userprofile') # Añadido related_name
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT) # Ya existe
    rut = models.CharField(max_length=12, unique=True, default="00000000-0") # Ya existe
    telefono = models.CharField(max_length=30, blank=True) # PDF: opcional
    direccion = models.TextField(blank=True) # Mantenido, aunque no está en PDF Usuarios

    # --- Campos añadidos/modificados según PDF Usuarios ---
    # nombres/apellidos: Usar user.first_name y user.last_name
    # username/email: Usar user.username y user.email
    # rol: Se maneja a través de user.groups y el modelo Role
    estado = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVO') # PDF: requerido, default ACTIVO
    mfa_habilitado = models.BooleanField(default=False) # PDF: requerido, default 0
    # ultimo_acceso: Usar user.last_login (solo lectura)
    # sesiones_activas: Implementación avanzada, omitido por ahora
    area_unidad = models.CharField(max_length=100, blank=True) # PDF: opcional
    observaciones = models.TextField(blank=True) # PDF: opcional
    # --- Fin campos PDF ---

    def __str__(self):
        return f"{self.user.username} @ {self.organization.name}"

class Module(models.Model):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    def __str__(self): return self.name

class Role(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="role")
    def __str__(self): return self.group.name

class RoleModulePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="module_perms")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="role_perms")
    can_view = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_change = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ("role", "module")

    def __str__(self):
        perms = f"V:{int(self.can_view)} A:{int(self.can_add)} C:{int(self.can_change)} D:{int(self.can_delete)}"
        return f"{self.role} -> {self.module} ({perms})"