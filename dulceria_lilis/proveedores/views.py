# proveedores/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required # Proteger vistas
from .models import Supplier
from .forms import SupplierForm

@login_required
def proveedores_list(request):
    proveedores = Supplier.objects.all().order_by('razon_social')
    context = {'proveedores': proveedores}
    return render(request, 'proveedores/proveedores_list.html', context)

@login_required
def proveedor_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado correctamente.')
            return redirect('proveedores:list') # Redirige a la lista
        else:
            messages.error(request, 'Error al crear el proveedor.')
    else:
        form = SupplierForm()
    context = {'form': form, 'is_new': True}
    return render(request, 'proveedores/proveedor_form.html', context)

@login_required
def proveedor_update(request, pk):
    proveedor = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado correctamente.')
            return redirect('proveedores:list')
        else:
            messages.error(request, 'Error al actualizar el proveedor.')
    else:
        form = SupplierForm(instance=proveedor)
    context = {'form': form, 'is_new': False, 'proveedor': proveedor}
    return render(request, 'proveedores/proveedor_form.html', context)

# Podrías añadir una vista para eliminar (proveedor_delete)