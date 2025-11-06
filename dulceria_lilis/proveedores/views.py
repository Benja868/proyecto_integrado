from django.contrib.auth.decorators import login_required, permission_required 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Supplier
from .forms import SupplierForm
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import openpyxl

@login_required
@permission_required('proveedores.view_supplier', raise_exception=True)
def proveedores_list(request):
    """
    Listado con:
    - filtro por texto (nombre, contacto, email, teléfono, dirección)
    - paginación
    - tamaño de página recordado en sesión
    """
    # --- 1) Leer query de búsqueda (persistimos en GET, no en sesión) ---
    q = (request.GET.get("q") or "").strip()

    # --- 2) Page size recordado en sesión ---
    # prioridad: GET -> sesión -> default
    if "page_size" in request.GET:
        try:
            page_size = int(request.GET.get("page_size", "10"))
        except ValueError:
            page_size = 10
        # normalizar opciones válidas
        if page_size not in (5, 10, 15, 30, 50, 100):
            page_size = 10
        request.session["proveedores_page_size"] = page_size
    else:
        page_size = int(request.session.get("proveedores_page_size", 10))

    # --- 3) Construir queryset filtrado ---
    qs = Supplier.objects.all().order_by("id")
    if q:
        qs = qs.filter(
        Q(razon_social__icontains=q) |
        Q(nombre_fantasia__icontains=q) |
        Q(contacto_principal_nombre__icontains=q) |
        Q(contacto_principal_email__icontains=q) |
        Q(contacto_principal_telefono__icontains=q) |
        Q(email__icontains=q) |
        Q(telefono__icontains=q) |
        Q(direccion__icontains=q)
    )

    # --- 4) Paginación ---
    paginator = Paginator(qs, page_size)
    page = request.GET.get("page") or 1
    try:
        proveedores = paginator.page(page)
    except PageNotAnInteger:
        proveedores = paginator.page(1)
    except EmptyPage:
        proveedores = paginator.page(paginator.num_pages)

    context = {
        "proveedores": proveedores,
        "q": q,
        "page_size": page_size,
        "page_sizes": (5, 10, 15, 30, 50, 100),
        "total": qs.count(),
    }
    return render(request, "proveedores/proveedores_list.html", context)

@login_required
@permission_required('proveedores.add_supplier', raise_exception=True)
def proveedor_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado correctamente.')
            return redirect('proveedores:list')
        messages.error(request, 'Corrige los errores.')
    else:
        form = SupplierForm()
    return render(request, 'proveedores/proveedor_form.html', {'form': form, 'modo': 'crear'})

@login_required
@permission_required('proveedores.change_supplier', raise_exception=True)
def proveedor_update(request, pk):
    proveedor = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado.')
            return redirect('proveedores:list')
        messages.error(request, 'Corrige los errores.')
    else:
        form = SupplierForm(instance=proveedor)
    return render(request, 'proveedores/proveedor_form.html', {'form': form, 'modo': 'editar'})

@login_required
@permission_required('proveedores.delete_supplier', raise_exception=True)
def proveedor_delete(request, pk):
    proveedor = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, 'Proveedor eliminado.')
        return redirect('proveedores:list')
    return render(request, 'proveedores/proveedores_confirm_delete.html', {'obj': proveedor})

# ✅ EXPORTAR PROVEEDORES A EXCEL (versión corregida)
@login_required
@permission_required('proveedores.view_supplier', raise_exception=True)
def exportar_proveedores_excel(request):
    proveedores = Supplier.objects.all().order_by('id')

    # Crear el archivo Excel
    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = "Proveedores"

    # Encabezados
    encabezados = [
        "ID",
        "RUT / NIF",
        "Razón Social",
        "Nombre Fantasía",
        "Email",
        "Teléfono",
        "Sitio Web",
        "Dirección",
        "Ciudad",
        "País",
        "Condiciones de Pago",
        "Moneda",
        "Contacto Principal",
        "Correo Contacto",
        "Teléfono Contacto",
        "Estado",
        "Observaciones",
    ]
    hoja.append(encabezados)

    # Datos (coinciden con los campos reales del modelo)
    for proveedor in proveedores:
        hoja.append([
            proveedor.id,
            proveedor.rut_nif,
            proveedor.razon_social,
            proveedor.nombre_fantasia,
            proveedor.email,
            proveedor.telefono,
            proveedor.sitio_web,
            proveedor.direccion,
            proveedor.ciudad,
            proveedor.pais,
            proveedor.condiciones_pago,
            proveedor.moneda,
            proveedor.contacto_principal_nombre,
            proveedor.contacto_principal_email,
            proveedor.contacto_principal_telefono,
            proveedor.estado,
            proveedor.observaciones,
        ])

    # Configurar respuesta HTTP
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="proveedores.xlsx"'
    workbook.save(response)
    return response
