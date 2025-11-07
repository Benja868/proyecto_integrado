from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin # Para proteger CBVs
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q # <<<--- AÑADIR ESTA IMPORTACIÓN
from .models import Product, Category
from .forms import ProductForm # Importar el formulario

# --- Vistas del Catálogo Público ---
def catalogo_principal(request):
    categorias = Category.objects.all().order_by('name')
    context = {'categorias': categorias}
    return render(request, 'catalogo/catalogo_principal.html', context)

def subcatalogo(request, categoria_slug):
    categoria = get_object_or_404(Category, name=categoria_slug) # O usar slug
    productos = Product.objects.filter(category=categoria).order_by('name')
    context = {'categoria': categoria, 'productos': productos}
    return render(request, 'catalogo/subcatalogo.html', context)

def detalle_producto(request, categoria_slug, producto_slug):
    categoria = get_object_or_404(Category, name=categoria_slug)
    producto = get_object_or_404(Product, category=categoria, sku=producto_slug)
    # TODO: Obtener stock_actual de inventario.services.get_stock(producto.id)
    stock_actual = 0 # Placeholder
    context = {
        'categoria': categoria,
        'producto': producto,
        'stock_actual': stock_actual,
    }
    return render(request, 'catalogo/detalle_producto.html', context)

# --- Vistas CRUD para Gestión de Productos ---

class ProductListView(ListView):
    model = Product
    template_name = "catalogo/productos_list.html"
    context_object_name = "productos"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # --- Búsqueda dinámica ---
        q = self.request.GET.get("q", "").strip()
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) |
                Q(descripcion__icontains=q) |
                Q(categoria__nombre__icontains=q)
            )

        # --- Ordenamiento dinámico ---
        sort_by = self.request.GET.get("sort_by", "id")
        queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["sort_by"] = self.request.GET.get("sort_by", "id")
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalogo/product_form.html'
    success_url = reverse_lazy('catalogo:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = True
        context['page_title'] = 'Crear Nuevo Producto'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Producto creado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el producto. Revisa el formulario.')
        return super().form_invalid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalogo/product_form.html'
    success_url = reverse_lazy('catalogo:product_list')
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = False
        context['page_title'] = f'Editar Producto: {self.object.name}'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el producto. Revisa el formulario.')
        return super().form_invalid(form)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'catalogo/product_confirm_delete.html'
    success_url = reverse_lazy('catalogo:product_list')
    pk_url_kwarg = 'pk'

    def form_valid(self, form): # Usar form_valid para añadir mensaje antes de borrar
        messages.success(self.request, f'Producto "{self.object.name}" eliminado correctamente.')
        return super().form_valid(form)

