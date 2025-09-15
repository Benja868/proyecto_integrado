from django.shortcuts import render
from .data import catalogos

def catalogo_principal(request):
    context = {
        'categorias': catalogos.keys()
    }
    return render(request, 'catalogo/catalogo_principal.html', context)

def subcatalogo(request, categoria):
    if categoria in catalogos:
        productos = catalogos[categoria]['productos']
        context = {
            'categoria': categoria,
            'productos': productos
        }
        return render(request, 'catalogo/subcatalogo.html', context)
    else:
        # Redirigir a página de error o al catálogo principal
        return catalogo_principal(request)

def detalle_producto(request, categoria, producto_id):
    if categoria in catalogos and producto_id in catalogos[categoria]['productos']:
        producto = catalogos[categoria]['productos'][producto_id]
        context = {
            'categoria': categoria,
            'producto_id': producto_id,
            'producto': producto
        }
        return render(request, 'catalogo/detalle_producto.html', context)
    else:
        # Redirigir a subcatálogo
        return subcatalogo(request, categoria)