# accounts/management/commands/seed_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

# Apps donde aplicaremos permisos para el Supervisor (ver/cambiar)
SUPERVISOR_APPS = [
    "proveedores",
    "catalogo",
    "inventario",
    "core",       # si quieres que edite compras/ventas/producción/finanzas
    "usuarios",   # solo ver/cambiar usuarios (no crear/borrar)
]

class Command(BaseCommand):
    help = "Crea los grupos: Administrador, Supervisor y Operador con sus permisos."

    def handle(self, *args, **options):
        # 1) Administrador
        admin_group, _ = Group.objects.get_or_create(name="Administrador")
        all_perms = Permission.objects.all()
        admin_group.permissions.set(all_perms)
        self.stdout.write(self.style.SUCCESS("Grupo 'Administrador' => TODOS los permisos."))

        # 2) Supervisor: view_* y change_* en las apps listadas
        supervisor_group, _ = Group.objects.get_or_create(name="Supervisor")
        supervisor_perms = Permission.objects.none()

        for app_label in SUPERVISOR_APPS:
            for model in apps.get_app_config(app_label).get_models():
                ct = ContentType.objects.get_for_model(model)
                perms = Permission.objects.filter(content_type=ct, codename__startswith='view_') | \
                        Permission.objects.filter(content_type=ct, codename__startswith='change_')
                supervisor_perms = supervisor_perms | perms

        supervisor_group.permissions.set(supervisor_perms.distinct())
        self.stdout.write(self.style.SUCCESS("Grupo 'Supervisor' => view_* y change_* en apps configuradas."))

        # 3) Operador: puede solo crear usuarios (add_usuario) y ver (view_usuario)
        operador_group, _ = Group.objects.get_or_create(name="Operador")
        try:
            usuario_ct = ContentType.objects.get(app_label="usuarios", model="usuario")
            add_user_perm = Permission.objects.get(content_type=usuario_ct, codename="add_usuario")
            view_user_perm = Permission.objects.get(content_type=usuario_ct, codename="view_usuario")
            operador_group.permissions.set([add_user_perm, view_user_perm])
            self.stdout.write(self.style.SUCCESS("Grupo 'Operador' => add_usuario, view_usuario."))
        except ContentType.DoesNotExist:
            self.stdout.write(self.style.ERROR("No se encontró ContentType usuarios.Usuario. Revisa AUTH_USER_MODEL."))
        except Permission.DoesNotExist:
            self.stdout.write(self.style.ERROR("No se encontraron permisos add/view para usuarios.Usuario."))

        self.stdout.write(self.style.SUCCESS("✔ Roles creados/actualizados con éxito."))
