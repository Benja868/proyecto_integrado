from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from accounts.models import Module, Role, RoleModulePermission, Organization
from django.db import transaction

class Command(BaseCommand):
    help = "Crea roles, módulos, permisos y un usuario admin por defecto para Dulcería Lilis"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Crear organización principal
        org, _ = Organization.objects.get_or_create(name="Dulcería Lilis",)

        # Crear módulos del sistema
        modules_data = [
            {"code": "ventas", "name": "Ventas"},
            {"code": "stock", "name": "Gestión de Stock"},
            {"code": "reportes", "name": "Reportes y Estadísticas"},
        ]

        for mod in modules_data:
            Module.objects.get_or_create(code=mod["code"], defaults={"name": mod["name"]})

        ventas = Module.objects.get(code="ventas")
        stock = Module.objects.get(code="stock")
        reportes = Module.objects.get(code="reportes")

        # Crear roles (grupos de Django)
        groups = {
            "Admin Dulcería": {"modules": [ventas, stock, reportes], "perms": (True, True, True, True)},
            "Jefe de Ventas": {"modules": [ventas, reportes], "perms": (True, True, True, False)},
            "Bodeguero": {"modules": [stock], "perms": (True, True, False, False)},
        }

        for name, data in groups.items():
            group, _ = Group.objects.get_or_create(name=name)
            role, _ = Role.objects.get_or_create(group=group)
            for mod in data["modules"]:
                RoleModulePermission.objects.get_or_create(
                    role=role,
                    module=mod,
                    defaults={
                        "can_view": data["perms"][0],
                        "can_add": data["perms"][1],
                        "can_change": data["perms"][2],
                        "can_delete": data["perms"][3],
                    }
                )

        # Crear usuario administrador
        if not User.objects.filter(username="adminlilis").exists():
            admin_user = User.objects.create_superuser(
                username="adminlilis",
                email="admin@lilis.com",
                password="admin123",
                first_name="Administrador",
                last_name="Lilis",
            )
            admin_user.groups.add(Group.objects.get(name="Admin Dulcería"))
            self.stdout.write(self.style.SUCCESS("👤 Usuario administrador creado correctamente."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Usuario adminlilis ya existe."))

        self.stdout.write(self.style.SUCCESS("✅ Roles, módulos y permisos creados correctamente."))
