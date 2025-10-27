# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Cliente, Producto, Compra, Venta, Produccion, Finanzas, Proveedor
from .forms import ClienteForm, ProductoForm, CompraForm, VentaForm, ProduccionForm, FinanzasForm

def home(request):
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    # métricas simples usando conteos
    ventas_count = Venta.objects.count()
    productos_stock = Producto.objects.count()
    pedidos_pendientes = Compra.objects.filter(total__isnull=False).count()
    bajo_stock = Producto.objects.filter(stock__lt=5).count()
    context = {
        'ventas_count': ventas_count,
        'productos_stock': productos_stock,
        'pedidos_pendientes': pedidos_pendientes,
        'bajo_stock': bajo_stock,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def clientes(request):
    form = ClienteForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado correctamente.')
            return redirect('clientes')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    clientes_qs = Cliente.objects.all().order_by('-fecha_registro')
    return render(request, 'core/clientes.html', {'form': form, 'clientes': clientes_qs})

@login_required
def inventario(request):
    form = ProductoForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado/actualizado correctamente.')
            return redirect('inventario')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    productos = Producto.objects.all().order_by('categoria', 'nombre')
    return render(request, 'core/inventario.html', {'form': form, 'productos': productos})

@login_required
def compras(request):
    form = CompraForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            compra = form.save()
            # actualizar stock del producto
            producto = compra.producto
            producto.stock += compra.cantidad
            producto.save()
            messages.success(request, 'Compra registrada y stock actualizado.')
            return redirect('compras')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    compras_qs = Compra.objects.select_related('producto').all().order_by('-fecha_compra')
    return render(request, 'core/compras.html', {'form': form, 'compras': compras_qs})

@login_required
def produccion(request):
    form = ProduccionForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            prod = form.save()
            # actualizar stock
            producto = prod.producto
            producto.stock += prod.cantidad_producida
            producto.save()
            messages.success(request, 'Producción registrada y stock actualizado.')
            return redirect('produccion')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    producciones = Produccion.objects.select_related('producto').all().order_by('-fecha_produccion')
    return render(request, 'core/produccion.html', {'form': form, 'producciones': producciones})

@login_required
def ventas(request):
    form = VentaForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            venta = form.save()
            # restar stock
            producto = venta.producto
            producto.stock = max(0, producto.stock - venta.cantidad)
            producto.save()
            messages.success(request, 'Venta registrada y stock actualizado.')
            return redirect('ventas')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    ventas_qs = Venta.objects.select_related('producto').all().order_by('-fecha_venta')
    return render(request, 'core/ventas.html', {'form': form, 'ventas': ventas_qs})

@login_required
def finanzas(request):
    form = FinanzasForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro financiero guardado.')
            return redirect('finanzas')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    registros = Finanzas.objects.all().order_by('-fecha')
    # resumen simple
    total_ingresos = sum(r.ingreso for r in registros)
    total_gastos = sum(r.gasto for r in registros)
    balance = total_ingresos - total_gastos
    return render(request, 'core/finanzas.html', {'form': form, 'registros': registros, 'balance': balance, 'total_ingresos': total_ingresos, 'total_gastos': total_gastos})

# Vista para listar proveedores
def proveedores(request):
    proveedores = Proveedor.objects.all()  # <-- Trae todos los registros desde MySQL
    return render(request, 'core/proveedores.html', {'proveedores': proveedores})

# Vista para listar productos
def productos(request):
    productos = Producto.objects.select_related('proveedor').all()  # <-- Incluye proveedor asociado
    return render(request, 'core/productos.html', {'productos': productos})