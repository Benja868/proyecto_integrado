# inventario/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import InventoryMovement, InventoryStock
from .forms import InventoryMovementForm


# =========================
# LISTADO DE MOVIMIENTOS
# =========================
@login_required
def movement_list(request):
    q = (request.GET.get("q") or "").strip()
    sort_by = request.GET.get("sort_by", "-id")

    movimientos = InventoryMovement.objects.select_related(
        "movement_type", "product", "uom", "warehouse", "created_by"
    )

    if q:
        movimientos = movimientos.filter(
            Q(product__name__icontains=q)
            | Q(movement_type__name__icontains=q)
            | Q(warehouse__name__icontains=q)
            | Q(created_by__username__icontains=q)
        )

    movimientos = movimientos.order_by(sort_by)

    paginator = Paginator(movimientos, 15)
    page = request.GET.get("page")
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        "page_obj": page_obj,
        "q": q,
        "sort_by": sort_by,
        "total": movimientos.count(),
    }
    return render(request, "inventario/movement_list.html", context)


# =========================
# CREAR MOVIMIENTO
# =========================
@login_required
def movement_create(request):
    if request.method == "POST":
        form = InventoryMovementForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    movement = form.save(commit=False)
                    movement.created_by = request.user
                    movement.save()

                    stock_entry, _ = InventoryStock.objects.get_or_create(
                        product=movement.product,
                        warehouse=movement.warehouse,
                    )

                    quantity_in_base_uom = movement.quantity
                    if movement.movement_type.is_entry:
                        stock_entry.quantity += quantity_in_base_uom
                    else:
                        if stock_entry.quantity < quantity_in_base_uom:
                            raise ValueError("Stock insuficiente para realizar la salida.")
                        stock_entry.quantity -= quantity_in_base_uom

                    stock_entry.save()
                    messages.success(request, "Movimiento de inventario registrado correctamente.")
                    return redirect("inventario:list")

            except Exception as e:
                messages.error(request, f"Error al registrar el movimiento: {e}")
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        form = InventoryMovementForm()

    context = {"form": form}
    return render(request, "inventario/movement_form.html", context)


# =========================
# CONSULTA DE STOCK
# =========================
@login_required
def stock_list(request):
    q = (request.GET.get("q") or "").strip()
    sort_by = request.GET.get("sort_by", "product__name")

    stocks = InventoryStock.objects.select_related("product", "warehouse")

    if q:
        stocks = stocks.filter(
            Q(product__name__icontains=q)
            | Q(warehouse__name__icontains=q)
        )

    stocks = stocks.filter(quantity__gt=0).order_by(sort_by)

    paginator = Paginator(stocks, 20)
    page = request.GET.get("page")
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        "page_obj": page_obj,
        "q": q,
        "sort_by": sort_by,
        "total": stocks.count(),
    }
    return render(request, "inventario/stock_list.html", context)
