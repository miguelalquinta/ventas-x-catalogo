from django.contrib import admin
from .models import Producto, ProductoCampana


class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa')
    search_fields = ('nombre',)  # Permite búsqueda al escribir en el campo producto

    def get_search_results(self, request, queryset, search_term):
        """Filtrar productos que NO están asignados a campañas abiertas"""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        # Excluir productos ya asignados a campañas abiertas
        productos_asignados = ProductoCampana.objects.filter(
            campana__activa=True
        ).values_list('producto_id', flat=True)
        queryset = queryset.exclude(id__in=productos_asignados)
        
        return queryset, use_distinct


class ProductoCampanaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'campana', 'precio_formateado', 'costo_formateado', 'ganancia_formateada')
    list_filter = ('campana',)
    search_fields = ('producto__nombre',)
    autocomplete_fields = ('producto',)  # Permite búsqueda con autocompletado mostrando el nombre

    # 💰 FORMATO $
    def precio_formateado(self, obj):
        return f"${obj.precio:,}".replace(",", ".")

    def costo_formateado(self, obj):
        return f"${obj.costo:,}".replace(",", ".")

    def ganancia_formateada(self, obj):
        return f"${obj.ganancia():,}".replace(",", ".")

    precio_formateado.short_description = "Precio"
    costo_formateado.short_description = "Costo"
    ganancia_formateada.short_description = "Ganancia"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'campana':
            # Filtrar solo campañas abiertas (activa=True)
            from campanas.models import Campana
            kwargs['queryset'] = Campana.objects.filter(activa=True).order_by('nombre')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Producto, ProductoAdmin)
admin.site.register(ProductoCampana, ProductoCampanaAdmin)
