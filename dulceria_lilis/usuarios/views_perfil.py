from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms_perfil import PerfilForm, CustomPasswordChangeForm

@login_required
def perfil_usuario(request):
    user = request.user
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('usuarios:perfil')
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        form = PerfilForm(instance=user)

    return render(request, 'usuarios/perfil.html', {'form': form})


@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect('usuarios:perfil')
        else:
            messages.error(request, "Corrige los errores en la contraseña.")
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'usuarios/cambiar_contrasena.html', {'form': form})
