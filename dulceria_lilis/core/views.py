# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.db.models import Sum, F, Q
import json

# Modelos de Core
from .models import Compra, Venta, Produccion, Finanzas
# Formularios de Core
from .forms import CompraForm, VentaForm, ProduccionForm, FinanzasForm

# Modelos de otras Apps necesarios
from catalogo.models import Product, UnitOfMeasure, Category
from proveedores.models import Supplier
from inventario.models import InventoryMovement, InventoryMovementType, Warehouse, InventoryStock

# Mixin buscador/paginador
from core.mixins import BusquedaPaginacionMixin


# --- Auxiliares Inventario ---
def _get_or_create_default_data():
    warehouse, unit_uom, mvt_types = None, None, {}
    try:
        warehouse, _ = Warehouse.objects.get_or_create(
            name="BOD-CENTRAL",
            defaults={'location': 'Bodega Principal por defecto'}
        )
    except Exception as e:
        print(f"[Inventario] Error creando/obteniendo bodega: {e}")

    try:
        unit_uom, _ = UnitOfMeasure.objects.get_or_create(
            code='UN',
            defaults={'name': 'Unidad'}
        )
    except Exception as e:
        print(f"[Inventario] Error creando/obteniendo UdM: {e}")

    mvt_types_codes = {
        'INGRESO_COMPRA': ('Ingreso por Compra', True),
        'SALIDA_VENTA': ('Salida por Venta', False),
        'INGRESO_PRODUCCION': ('Ingreso por Producción', True),
        'AJUSTE_POSITIVO': ('Ajuste Positivo', True),
        'AJUSTE_NEGATIVO': ('Ajuste Negativo', False),
    }
    try:
        for code, (name, is_entry) in mvt_types_codes.items():
            mvt_type, _ = InventoryMovementType.objects.get_or_create(
                code=code,
                defaults={'name': name, 'is_entry': is_entry}
            )
            mvt_types[code] = mvt_type
    except Exception as e:
        print(f"[Inventario] Error creando tipos movimiento: {e}")

    return warehouse, unit_uom, mvt_types


def _create_inventory_movement(mvt_type_code, product, quantity, warehouse, user, **kwargs):
    if not warehouse:
        raise ValueError("Error: Bodega no especificada para el movimiento.")

    _, _, mvt_types = _get_or_create_default_data()
    mvt_type = mvt_types.get(mvt_type_code) or InventoryMovementType.objects.get(code=mvt_type_code)

    base_uom = getattr(product, "uom_sale", None)
    if not base_uom:
        raise ValueError("El producto no tiene UdM de Venta definida.")

    if quantity <= 0:
        raise ValueError("La cantidad del movimiento debe ser mayor que cero.")

    try:
        with transaction.atomic():
            stock_entry, _ = InventoryStock.objects.get_or_create(
                product=product, warehouse=warehouse, defaults={'quantity': 0}
            )

            qty = quantity  # ya en UdM base

            if not mvt_type.is_entry:
                if stock_entry.quantity < qty:
                    raise IntegrityError(
                        f"Stock insuficiente para {getattr(product, 'sku', product)} en {warehouse.name}. "
                        f"Stock: {stock_entry.quantity} {base_uom.code}, Requerido: {qty} {base_uom.code}."
                    )
                stock_entry.quantity -= qty
            else:
                stock_entry.quantity += qty

            stock_entry.save()

            valid_kwargs = {k: v for k, v in kwargs.items() if hasattr(InventoryMovement, k)}
            movement = InventoryMovement.objects.create(
                movement_type=mvt_type, product=product, quantity=quantity,
                uom=base_uom, warehouse=warehouse, created_by=user, **valid_kwargs
            )
            return movement

    except IntegrityError as e:
        raise IntegrityError(str(e))
    except Exception as e:
        raise ValueError(f"Error al procesar movimiento de inventario: {e}")


# --- Vistas ---
def home(request):
    return render(request, 'core/home.html')


@login_required
def dashboard(request):
    today = timezone.now().date()
    warehouse_default, _, _ = _get_or_create_default_data()

    ventas_hoy_count = 0
    ventas_hoy_total = 0
    stock_total_items = 0
    pedidos_pendientes_count = 0
    bajo_stock_count = 0
    warehouse_name = warehouse_default.name if warehouse_default else "N/A"

    # ========== MÉTRICAS PRINCIPALES ==========
    if not warehouse_default:
        messages.error(request, "Error: Bodega por defecto 'BOD-CENTRAL' no encontrada. Cree la bodega en el admin.")
    else:
        try:
            ventas_hoy = Venta.objects.filter(fecha_venta=today)
            ventas_hoy_count = ventas_hoy.count()
            ventas_hoy_total = ventas_hoy.aggregate(total=Sum('total'))['total'] or 0
        except Exception as e:
            messages.warning(request, f"Advertencia: No se pudieron calcular las ventas de hoy ({e}).")

        try:
            stock_total_items = InventoryStock.objects.filter(
                warehouse=warehouse_default
            ).aggregate(total=Sum('quantity'))['total'] or 0
        except Exception as e:
            messages.warning(request, f"Advertencia: No se pudo calcular el stock total ({e}).")

        try:
            bajo_stock_count = InventoryStock.objects.filter(
                warehouse=warehouse_default,
                product__stock_min__isnull=False,
                quantity__lte=F('product__stock_min'),
                quantity__gt=0
            ).count()
        except Exception as e:
            messages.warning(request, f"Advertencia: No se pudo calcular el bajo stock ({e}). Verifique el modelo Product.")

    # ========== GRÁFICO DE VENTAS (ÚLTIMOS 7 DÍAS) ==========
    ultimos_dias = [today - timezone.timedelta(days=i) for i in range(6, -1, -1)]
    ventas_diarias = (
        Venta.objects.filter(fecha_venta__in=ultimos_dias)
        .annotate(dia=TruncDate('fecha_venta'))
        .values('dia')
        .annotate(total=Sum('total'))
        .order_by('dia')
    )

    ventas_labels = [v['dia'].strftime("%d-%m") for v in ventas_diarias]
    ventas_data = [float(v['total']) for v in ventas_diarias]

    # ========== GRÁFICO DE STOCK POR CATEGORÍA ==========
    stock_por_categoria = (
        InventoryStock.objects.filter(warehouse=warehouse_default)
        .values('product__category__name')
        .annotate(total=Sum('quantity'))
        .order_by('-total')[:5]
    )
    stock_labels = [s['product__category__name'] or "Sin categoría" for s in stock_por_categoria]
    stock_data = [s['total'] for s in stock_por_categoria]

    # ========== CONTEXTO ==========
    ctx = {
        'ventas_hoy_count': ventas_hoy_count,
        'ventas_hoy_total': ventas_hoy_total,
        'stock_total_items': stock_total_items,
        'pedidos_pendientes_count': pedidos_pendientes_count,
        'bajo_stock_count': bajo_stock_count,
        'warehouse_name': warehouse_name,

        # datos JSON para los gráficos
        'ventas_labels': json.dumps(ventas_labels),
        'ventas_data': json.dumps(ventas_data),
        'stock_labels': json.dumps(stock_labels),
        'stock_data': json.dumps(stock_data),
    }

    return render(request, 'core/dashboard.html', ctx)


# ===============================================================
# =================== VISTAS CON ORDEN Y BÚSQUEDA ===============
# ===============================================================
@login_required
def compras(request):
    form = CompraForm(request.POST or None, initial={'fecha_compra': timezone.now().date()})

    # --- Registrar compra ---
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                compra = form.save(commit=False)
                if not compra.proveedor_id:
                    messages.error(request, 'Debe seleccionar un proveedor.')
                    raise ValueError("Proveedor no seleccionado")
                compra.save()

                warehouse, _, _ = _get_or_create_default_data()
                _create_inventory_movement(
                    mvt_type_code='INGRESO_COMPRA',
                    product=compra.producto,
                    quantity=compra.cantidad,
                    warehouse=warehouse,
                    user=request.user,
                    unit_cost=(compra.total / compra.cantidad) if compra.cantidad > 0 else 0,
                    supplier=compra.proveedor,
                    doc_reference=compra.doc_referencia
                )
                messages.success(request, 'Compra registrada y stock actualizado.')
                return redirect('compras')
        except Exception as e:
            messages.error(request, f'Error al registrar la compra: {e}')

    # --- Búsqueda + Orden + Paginación ---
    q = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort_by', '-fecha_compra')

    mix = BusquedaPaginacionMixin(request, search_fields=["producto__nombre", "proveedor__razon_social", "doc_referencia"], paginate_by=10)
    compras_qs = mix.aplicar(Compra.objects.select_related('producto', 'proveedor').all().order_by(sort_by))

    return render(request, 'core/compras.html', {
        'form': form, 'page_obj': compras_qs, 'q': q, 'sort_by': sort_by
    })


@login_required
def produccion(request):
    form = ProduccionForm(request.POST or None, initial={'fecha_produccion': timezone.now().date()})

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
                messages.success(request, 'Producción registrada y stock actualizado.')
                return redirect('produccion')
        except Exception as e:
            messages.error(request, f'Error al registrar la producción: {e}')

    q = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort_by', '-fecha_produccion')

    mix = BusquedaPaginacionMixin(request, search_fields=["producto__nombre"], paginate_by=10)
    producciones = mix.aplicar(Produccion.objects.select_related('producto').all().order_by(sort_by))

    return render(request, 'core/produccion.html', {'form': form, 'page_obj': producciones, 'q': q, 'sort_by': sort_by})


@login_required
def ventas(request):
    form = VentaForm(request.POST or None, initial={'fecha_venta': timezone.now().date()})

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
                messages.success(request, 'Venta registrada y stock actualizado.')
                return redirect('ventas')
        except Exception as e:
            messages.error(request, f'Error al registrar la venta: {e}')

    q = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort_by', '-fecha_venta')

    mix = BusquedaPaginacionMixin(request, search_fields=["producto__nombre", "doc_referencia"], paginate_by=10)
    ventas_qs = mix.aplicar(Venta.objects.select_related('producto').all().order_by(sort_by))

    return render(request, 'core/ventas.html', {'form': form, 'page_obj': ventas_qs, 'q': q, 'sort_by': sort_by})


@login_required
def finanzas(request):
    form = FinanzasForm(request.POST or None, initial={'fecha': timezone.now().date()})

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Registro financiero guardado.')
        return redirect('finanzas')

    q = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort_by', '-fecha')

    mix = BusquedaPaginacionMixin(request, search_fields=["descripcion"], paginate_by=12)
    registros_page = mix.aplicar(Finanzas.objects.all().order_by(sort_by))

    totals = Finanzas.objects.aggregate(
        total_ingresos=Sum('ingreso', filter=Q(ingreso__isnull=False)),
        total_gastos=Sum('gasto', filter=Q(gasto__isnull=False))
    )

    balance = (totals.get('total_ingresos', 0) or 0) - (totals.get('total_gastos', 0) or 0)

    return render(request, 'core/finanzas.html', {
        'form': form,
        'page_obj': registros_page,
        'q': q,
        'sort_by': sort_by,
        'balance': balance,
        'total_ingresos': totals.get('total_ingresos', 0) or 0,
        'total_gastos': totals.get('total_gastos', 0) or 0,
    })
