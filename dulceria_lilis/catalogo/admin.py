from django.contrib import admin, messages
from .models import Category, Product, AlertRule, ProductAlertRule
from .forms import ProductForm


# Inline de productos dentro de categoría
class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ("name", "price", "stock")
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    inlines = [ProductInline]


# Acciones personalizadas
@admin.action(description="Marcar productos como AGOTADOS")
def make_out_of_stock(modeladmin, request, queryset):
    updated = queryset.update(stock=0, available=False)
    modeladmin.message_user(
        request,
        f"Se marcaron {updated} productos como sin stock.",
        level=messages.WARNING
    )


@admin.action(description="Aplicar descuento del 10%%")
def apply_discount(modeladmin, request, queryset):
    updated = 0
    for product in queryset:
        if product.price:  # aseguramos que tenga precio
            product.price = round(product.price * 0.9, 2)
            product.save()
            updated += 1
    modeladmin.message_user(
        request,
        f"Se aplicó un 10% de descuento a {updated} productos.",
        level=messages.SUCCESS
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "stock", "available")
    search_fields = ("name", "sku", "category__name")
    list_filter = ("category", "available")
    ordering = ("category", "name")
    actions = [make_out_of_stock, apply_discount]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Si tus productos tienen relación con organization:
        return qs.filter(category__organization=request.user.userprofile.organization)
