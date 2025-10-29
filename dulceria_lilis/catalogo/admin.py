from django.contrib import admin, messages
# Asegúrate de importar TODOS los modelos que quieres registrar
from .models import Category, Product, AlertRule, ProductAlertRule, Brand, UnitOfMeasure
from .forms import ProductForm
# Si necesitas la relación con proveedores aquí (ej. inlines)
# from proveedores.models import ProductSupplier

# --- Inlines (Opcional, si quieres editar productos desde Categoría) ---
# class ProductInline(admin.TabularInline):
#     model = Product
#     extra = 0
#     fields = ("name", "sku", "sale_price", "available") # Usar sale_price, quitar stock
#     readonly_fields = ("sku",) # SKU usualmente no se edita aquí
#     show_change_link = True

# --- Registros de Modelos Simples ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    # inlines = [ProductInline] # Descomentar si usas el inline

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)

@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    ordering = ("name",)

@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "severity")
    list_filter = ("severity",)

@admin.register(ProductAlertRule)
class ProductAlertRuleAdmin(admin.ModelAdmin):
    list_display = ("product", "alert_rule", "min_value", "max_value")
    list_filter = ("alert_rule",)
    autocomplete_fields = ['product'] # Mejora la selección de producto


# --- Acciones Personalizadas para ProductAdmin (Ajustadas) ---
@admin.action(description="Marcar productos como NO DISPONIBLES")
def make_unavailable(modeladmin, request, queryset):
    # Ya no se modifica 'stock', solo 'available'
    updated = queryset.update(available=False)
    modeladmin.message_user(
        request,
        f"Se marcaron {updated} productos como NO disponibles.",
        level=messages.WARNING
    )

@admin.action(description="Marcar productos como DISPONIBLES")
def make_available(modeladmin, request, queryset):
    updated = queryset.update(available=True)
    modeladmin.message_user(
        request,
        f"Se marcaron {updated} productos como DISPONIBLES.",
        level=messages.SUCCESS
    )


@admin.action(description="Aplicar descuento del 10%% al Precio Base")
def apply_discount_10_percent(modeladmin, request, queryset):
    updated = 0
    for product in queryset:
        if product.sale_price is not None: # Usar sale_price
            product.sale_price = round(product.sale_price * 0.9, 2) # Redondear a 2 decimales
            product.save()
            updated += 1
    modeladmin.message_user(
        request,
        f"Se aplicó un 10% de descuento al precio base de {updated} productos.",
        level=messages.SUCCESS
    )


# --- Registro del Modelo Product (Corregido) ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm # Usar el formulario personalizado si tiene validaciones útiles
    # CORREGIDO: Usar 'sale_price' en lugar de 'price', eliminar 'stock'
    list_display = ("name", "sku", "category", "sale_price", "available")
    search_fields = ("name", "sku", "category__name", "brand__name") # Añadido brand
    list_filter = ("category", "brand", "available", "is_perishable", "lot_controlled", "serial_controlled") # Añadidos filtros
    ordering = ("category", "name")
    actions = [make_unavailable, make_available, apply_discount_10_percent] # Acciones actualizadas
    autocomplete_fields = ['category', 'brand', 'uom_purchase', 'uom_sale'] # Facilitan selección

    # Organizar campos en pestañas/secciones para mejor visualización
    fieldsets = (
        ('Identificación', {
            'fields': ('name', 'sku', 'ean_upc', 'category', 'brand', 'model_name', 'description')
        }),
        ('Unidades y Precios', {
            'fields': ('uom_purchase', 'uom_sale', 'conversion_factor', 'standard_cost', 'sale_price', 'tax_rate')
        }),
        ('Control de Stock', {
            'fields': ('stock_min', 'stock_max', 'reorder_point', 'available')
        }),
        ('Control Avanzado', {
            'fields': ('is_perishable', 'lot_controlled', 'serial_controlled')
        }),
        ('Relaciones y Soporte', {
            'fields': ('image_url', 'datasheet_url'),
            'classes': ('collapse',) # Opcional: Colapsar esta sección
        }),
    )

    # Nota: get_queryset se eliminó porque la lógica de organización ahora está en UserProfile,
    # el admin de Django por defecto no filtra por organización. Si necesitas esa lógica,
    # deberás reintroducirla adaptándola a cómo relacionas productos con usuarios/organizaciones.
