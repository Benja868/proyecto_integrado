# core/mixins.py
from django.core.paginator import Paginator
from django.db.models import Q

class BusquedaPaginacionMixin:
    """
    Reutilizable en cualquier vista de listado.
    - search_fields: lista de campos para filtrar con icontains
    - paginate_by: tamaño de página
    """
    search_fields = []
    paginate_by = 10

    def __init__(self, request, search_fields=None, paginate_by=None):
        self.request = request
        if search_fields is not None:
            self.search_fields = search_fields
        if paginate_by is not None:
            self.paginate_by = paginate_by

    def filtrar(self, queryset):
        q = self.request.GET.get("q", "").strip()
        if q and self.search_fields:
            cond = Q()
            for field in self.search_fields:
                cond |= Q(**{f"{field}__icontains": q})
            queryset = queryset.filter(cond)
        return queryset

    def paginar(self, queryset):
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get("page")
        return paginator.get_page(page_number)

    def aplicar(self, queryset):
        return self.paginar(self.filtrar(queryset))
