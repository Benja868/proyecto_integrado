# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.db.models import Sum, F, Q

# Modelos de Core
from .models import Compra, Venta, Produccion, Finanzas

# Formularios
from .forms import CompraForm, VentaForm, ProduccionForm, FinanzasForm

# Modelos de otras Apps necesarios
from catalogo.models import Product, UnitOfMeasure
from proveedores.models import Supplier
from inventario.models import InventoryMovement, InventoryMovementType, Warehouse, InventoryStock


# --- Funciones Auxiliares ---
def _get_or_create_default_data():
    """Crea o obtiene datos base: bodega principal, unidad y tipos de movimiento."""
    warehouse, unit_uom, mvt_types = None, None, {}

    try:
        warehouse, _ = Warehouse.objects.get_or_create(
            name="BOD-CENTRAL",
            defaults={'location': 'Bodega Principal'}
        )
    except Exception as e:
        print(f"ERROR: No se pudo crear/obtener la bodega: {e}")

    try:
        unit_uom, _ = UnitOfMeasure.objects.get_or_create(
            code='UN', defaults={'name': 'Unidad'}
        )
    except Exception as e:
        print(f"ERROR: No se pudo crear/obtener la unidad de medida: {e}")

    # Tipos de movimiento base
    mvt_defs = {
        'INGRESO_COMPRA': ('Ingreso por Compra', True),
        'SALIDA_VENTA': ('Salida por Venta', False),
        'INGRESO_PRODUCCION': ('Ingreso por Producción', True),
        'AJUSTE_POSITIVO': ('Ajuste Positivo', True),
        'AJUSTE_NEGATIVO': ('Ajuste Negativo', False),
    }

    try:
        for code, (name, is_entry) in mvt_defs.items():
            obj, _ = InventoryMovementType.objects.get_or_create(
                code=code, defaults={'name': name, 'is_entry': is_entry}
            )
            mvt_types[code] = obj
    except Exception as e:
        print(f"ERROR: No se pudieron crear los tipos de movimiento: {e}")

    return warehouse, unit_uom, mvt_types


def _create_inventory_movement(mvt_type_code, product, quantity, warehouse, user, **kwargs):
    """Crea un movimiento de inventario y actualiza stock."""
    warehouse_default, _, mvt_types = _get_or_create_default_data()

    if not warehouse:
        raise ValueError("Debe especificar una bodega.")
    mvt_type = mvt_types.get(mvt_type_code)
    if not mvt_type:
        raise ValueError(f"Tipo de movimiento '{mvt_type_code}' no existe.")

    base_uom = product.uom_sale
    if not base_uom:
        raise ValueError(f"El producto {product.sku} no tiene unidad de venta definida.")

    if quantity <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")

    try:
        with transaction.atomic():
            stock_entry, _ = InventoryStock.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                defaults={'quantity': 0}
            )

            if mvt_type.is_entry:
                stock_entry.quantity += quantity
            else:
                if stock_entry.quantity < quantity:
                    raise IntegrityError(f"Stock insuficiente para {product.sku}.")
                stock_entry.quantity -= quantity

            stock_entry.save()

            valid_kwargs = {k: v for k, v in kwargs.items() if hasattr(InventoryMovement, k)}
            movement = InventoryMovement.objects.create(
                movement_type=mvt_type,
                product=product,
                quantity=quantity,
                uom=base_uom,
                warehouse=warehouse,
                created_by=user,
                **valid_kwargs
            )

            return movement

    except IntegrityError as e:
        raise IntegrityError(str(e))
    except Exception as e:
        raise ValueError(f"Error al crear movimiento: {e}")


# --- Vistas ---
def home(request):
    return render(request, 'core/home.html')


@login_required
def dashboard(request):
    """Panel principal de métricas."""
    today = timezone.now().date()
    warehouse_default, _, _ = _get_or_create_default_data()

    context = {
        'ventas_hoy_count': 0,
        'ventas_hoy_total': 0,
        'stock_total_items': 0,
        'pedidos_pendientes_count': 0,
        'bajo_stock_count': 0,
        'warehouse_name': warehouse_default.name if warehouse_default else "N/A",
    }

    try:
        ventas_hoy = Venta.objects.filter(fecha_venta=today)
        context['ventas_hoy_count'] = ventas_hoy.count()
        context['ventas_hoy_total'] = ventas_hoy.aggregate(total=Sum('total'))['total'] or 0
    except Exception as e:
        messages.warning(request, f"No se pudieron calcular las ventas de hoy ({e}).")

    try:
        context['stock_total_items'] = InventoryStock.objects.filter(
            warehouse=warehouse_default
        ).aggregate(total=Sum('quantity'))['total'] or 0
    except Exception as e:
        messages.warning(request, f"No se pudo calcular el stock total ({e}).")

    return render(request, 'core/dashboard.html', context)


@login_required
def compras(request):
    initial_data = {'fecha_compra': timezone.now().date()}
    form = CompraForm(request.POST or None, initial=initial_data)

    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                compra = form.save(commit=False)
                if not compra.proveedor_id:
                    messages.error(request, "Debe seleccionar un proveedor.")
                    raise ValueError("Proveedor no seleccionado")

                compra.save()
                warehouse, _, _ = _get_or_create_default_data()
                if not warehouse:
                    raise ValueError("Bodega por defecto no encontrada")

                _create_inventory_movement(
                    mvt_type_code='INGRESO_COMPRA',
                    product=compra.producto,
                    quantity=compra.cantidad,
                    warehouse=warehouse,
                    user=request.user,
                    unit_cost=compra.total / compra.cantidad if compra.cantidad > 0 else 0,
                    supplier=compra.proveedor,
                    doc_reference=compra.doc_referencia
                )
                messages.success(request, "Compra registrada y stock actualizado.")
                return redirect('compras')
        except Exception as e:
            messages.error(request, f"Error al registrar compra: {e}")

    compras_qs = Compra.objects.select_related('producto', 'proveedor').order_by('-fecha_compra')[:50]
    return render(request, 'core/compras.html', {'form': form, 'compras': compras_qs})


@login_required
def produccion(request):
    initial_data = {'fecha_produccion': timezone.now().date()}
    form = ProduccionForm(request.POST or None, initial=initial_data)

    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                prod = form.save()
                warehouse, _, _ = _get_or_create_default_data()
                _create_inventory_movement(
                    mvt_type_code='INGRESO_PRODUCCION',
                    product=prod.producto,
                    quantity=prod.cantidad_producida,
                    warehouse=warehouse,
                    user=request.user,
                )
                messages.success(request, "Producción registrada y stock actualizado.")
                return redirect('produccion')
        except Exception as e:
            messages.error(request, f"Error al registrar producción: {e}")

    producciones = Produccion.objects.select_related('producto').order_by('-fecha_produccion')[:50]
    return render(request, 'core/produccion.html', {'form': form, 'producciones': producciones})


@login_required
def ventas(request):
    initial_data = {'fecha_venta': timezone.now().date()}
    form = VentaForm(request.POST or None, initial=initial_data)

    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                venta = form.save()
                warehouse, _, _ = _get_or_create_default_data()
                _create_inventory_movement(
                    mvt_type_code='SALIDA_VENTA',
                    product=venta.producto,
                    quantity=venta.cantidad,
                    warehouse=warehouse,
                    user=request.user,
                    doc_reference=venta.doc_referencia
                )
                messages.success(request, "Venta registrada y stock actualizado.")
                return redirect('ventas')
        except IntegrityError:
            messages.error(request, "Error: stock insuficiente.")
        except Exception as e:
            messages.error(request, f"Error al registrar venta: {e}")

    ventas_qs = Venta.objects.select_related('producto').order_by('-fecha_venta')[:50]
    return render(request, 'core/ventas.html', {'form': form, 'ventas': ventas_qs})


@login_required
def finanzas(request):
    initial_data = {'fecha': timezone.now().date()}
    form = FinanzasForm(request.POST or None, initial=initial_data)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Registro financiero guardado.")
        return redirect('finanzas')

    registros = Finanzas.objects.all().order_by('-fecha')[:100]
    totals = registros.aggregate(
        total_ingresos=Sum('ingreso'),
        total_gastos=Sum('gasto')
    )
    balance = (totals.get('total_ingresos') or 0) - (totals.get('total_gastos') or 0)

    context = {
        'form': form,
        'registros': registros,
        'balance': balance,
        'total_ingresos': totals.get('total_ingresos') or 0,
        'total_gastos': totals.get('total_gastos') or 0,
    }
    return render(request, 'core/finanzas.html', context)
