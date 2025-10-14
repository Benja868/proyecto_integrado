from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

def inventario(request):
    return render(request, 'core/inventario.html')

def compras(request):
    return render(request, 'core/compras.html')

def produccion(request):
    return render(request, 'core/produccion.html')

def ventas(request):
    return render(request, 'core/ventas.html')

def finanzas(request):
    return render(request, 'core/finanzas.html')

def clientes(request):
    return render(request, 'core/clientes.html')