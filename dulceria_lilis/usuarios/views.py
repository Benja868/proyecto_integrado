from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import PasswordChangeForm
from core.utils import export_to_excel

from .forms import UsuarioForm, UsuarioEditForm


Usuario = get_user_model()


# ============================================================================================
# LISTADO DE USUARIOS
# ============================================================================================
@login_required
@permission_required('usuarios.view_usuario', raise_exception=True)
def usuarios_list(request):

    q = (request.GET.get("q") or "").strip()
    sort_by = request.GET.get("sort_by", "id")

    # Tamaño de página configurable desde la UI
    if "page_size" in request.GET:
        try:
            page_size = int(request.GET.get("page_size"))
        except ValueError:
            page_size = 10
        request.session["usuarios_page_size"] = page_size
    else:
        page_size = int(request.session.get("usuarios_page_size", 10))

    usuarios = Usuario.objects.all().order_by(sort_by)

    if q:
        usuarios = usuarios.filter(
            Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(email__icontains=q)
            | Q(telefono__icontains=q)
            | Q(rol__icontains=q)
        )

    paginator = Paginator(usuarios, page_size)
    page = request.GET.get("page") or 1

    try:
        usuarios_page = paginator.page(page)
    except PageNotAnInteger:
        usuarios_page = paginator.page(1)
    except EmptyPage:
        usuarios_page = paginator.page(paginator.num_pages)

    context = {
        "usuarios": usuarios_page,
        "q": q,
        "sort_by": sort_by,
        "page_size": page_size,
        "page_sizes": (5, 10, 15, 30, 50, 100),
        "total": usuarios.count(),
    }

    return render(request, "usuarios/usuarios_list.html", context)



# ============================================================================================
# CREAR USUARIO (CON CONTRASEÑA TEMPORAL)
# ============================================================================================
@login_required
@permission_required('usuarios.add_usuario', raise_exception=True)
def usuario_create(request):

    if request.method == 'POST':
        form = UsuarioForm(request.POST)

        if form.is_valid():
            # 1. Guardar el usuario con UserCreationForm (incluye contraseña correcta)
            usuario = form.save()

            # 2. Después del save, agregamos el flag para forzar cambio de contraseña
            usuario.password_must_change = True
            usuario.save()

            messages.success(
                request,
                "✅ Usuario creado correctamente. El usuario deberá cambiar su contraseña al iniciar sesión."
            )

            return redirect('usuarios:list')

        messages.error(request, "❌ Revisa los errores del formulario.")

    else:
        form = UsuarioForm()

    return render(request, 'usuarios/usuarios_form.html', {'form': form, 'modo': 'crear'})



# ============================================================================================
# EDITAR USUARIO
# ============================================================================================
@login_required
@permission_required('usuarios.change_usuario', raise_exception=True)
def usuario_update(request, pk):

    user = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            messages.success(request, "✅ Usuario actualizado correctamente.")
            return redirect('usuarios:list')

        messages.error(request, "❌ Revisa los errores del formulario.")

    else:
        form = UsuarioEditForm(instance=user)

    return render(request, 'usuarios/usuarios_form.html', {'form': form, 'modo': 'editar'})



# ============================================================================================
# ELIMINAR USUARIO
# ============================================================================================
@login_required
@permission_required('usuarios.delete_usuario', raise_exception=True)
def usuario_delete(request, pk):

    user = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        user.delete()
        messages.success(request, "🗑️ Usuario eliminado correctamente.")
        return redirect('usuarios:list')

    return render(request, 'usuarios/usuarios_confirm_delete.html', {"obj": user})



# ============================================================================================
# PERFIL DEL USUARIO
# ============================================================================================
@login_required
def perfil_usuario(request):

    user = request.user

    if request.method == 'POST':

        form = UsuarioEditForm(request.POST, request.FILES, instance=user)
        password_form = PasswordChangeForm(user, request.POST)

        if 'update_profile' in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, "✅ Perfil actualizado correctamente.")
                return redirect('usuarios:perfil')
            else:
                messages.error(request, "❌ Revisa los errores del formulario.")

        elif 'change_password' in request.POST:
            if password_form.is_valid():

                user = password_form.save()
                update_session_auth_hash(request, user)

                messages.success(request, "🔐 Contraseña cambiada correctamente.")
                return redirect('usuarios:perfil')

            else:
                messages.error(request, "❌ No se pudo cambiar la contraseña.")

    else:
        form = UsuarioEditForm(instance=user)
        password_form = PasswordChangeForm(user)

    return render(request, 'usuarios/perfil_usuario.html', {
        'form': form,
        'password_form': password_form,
        'usuario': user
    })



# ============================================================================================
# EXPORTAR USUARIOS A EXCEL
# ============================================================================================
def exportar_usuarios_excel(request):

    usuarios = Usuario.objects.all()

    headers = ["ID", "Usuario", "Nombre", "Email", "Rol", "Teléfono", "Activo", "Fecha registro"]

    data = [
        [
            u.id,
            u.username,
            f"{u.first_name} {u.last_name}",
            u.email,
            u.rol,
            u.telefono,
            "Sí" if u.estado else "No",
            u.date_joined.strftime("%Y-%m-%d"),
        ]
        for u in usuarios
    ]

    return export_to_excel(headers, data, "usuarios")
