# inventario/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction # Para atomicidad
from .models import InventoryMovement, InventoryStock # Importar modelos
from .forms import InventoryMovementForm

@login_required
def movement_list(request):
    movements = InventoryMovement.objects.select_related(
        'movement_type', 'product', 'uom', 'warehouse', 'created_by'
    ).all()[:100] # Limitar por rendimiento, añadir paginación luego
    context = {'movements': movements}
    return render(request, 'inventario/movement_list.html', context)

@login_required
def movement_create(request):
    if request.method == 'POST':
        form = InventoryMovementForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic(): # Asegura que el movimiento y el stock se actualicen juntos
                    movement = form.save(commit=False)
                    movement.created_by = request.user
                    movement.save()

                    # --- Actualizar InventoryStock (Simplificado) ---
                    # Esta lógica debería ir en signals.py o en un servicio dedicado
                    stock_entry, created = InventoryStock.objects.get_or_create(
                        product=movement.product,
                        warehouse=movement.warehouse
                        # Añadir Lote/Serie/Vencimiento si InventoryStock es granular
                    )

                    quantity_in_base_uom = movement.quantity # Asumir que el movimiento está en UdM base por ahora
                    # Si no, convertir: quantity_in_base_uom = movement.quantity * factor_conversion

                    if movement.movement_type.is_entry:
                        stock_entry.quantity += quantity_in_base_uom
                    else:
                        stock_entry.quantity -= quantity_in_base_uom
                    stock_entry.save()
                    # --- Fin Actualizar InventoryStock ---

                    messages.success(request, 'Movimiento de inventario registrado correctamente.')
                    return redirect('inventario:list') # Redirigir a la lista
            except Exception as e:
                messages.error(request, f'Error al registrar el movimiento: {e}')

        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = InventoryMovementForm()

    context = {'form': form}
    return render(request, 'inventario/movement_form.html', context)

# Vista para consultar stock (ejemplo simple)
@login_required
def stock_list(request):
    stocks = InventoryStock.objects.select_related('product', 'warehouse').filter(quantity__gt=0).order_by('warehouse__name', 'product__name')
    context = {'stocks': stocks}
    return render(request, 'inventario/stock_list.html', context)