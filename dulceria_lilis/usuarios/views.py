from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario
from .forms import UsuarioForm, UsuarioEditForm

@login_required
def usuarios_list(request):
    usuarios = Usuario.objects.all().order_by('username')
    return render(request, 'usuarios/usuarios_list.html', {'usuarios': usuarios})

@login_required
def usuarios_create(request):
    form = UsuarioForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect('usuarios:list')
        else:
            messages.error(request, "Corrige los errores del formulario.")
    return render(request, 'usuarios/usuarios_form.html', {'form': form, 'accion': 'Crear'})

@login_required
def usuarios_update(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioEditForm(request.POST or None, instance=usuario)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('usuarios:list')
        else:
            messages.error(request, "Corrige los errores del formulario.")
    return render(request, 'usuarios/usuarios_form.html', {'form': form, 'accion': 'Editar'})

@login_required
def usuarios_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")
        return redirect('usuarios:list')
    return render(request, 'usuarios/usuarios_confirm_delete.html', {'object': usuario})
