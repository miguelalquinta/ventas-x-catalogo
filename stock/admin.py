from django.contrib import admin
from .models import ProductoStock, MovimientoStock


@admin.action(description="➕ Agregar 10 unidades")
def agregar_stock_10(modeladmin, request, queryset):
    for producto in queryset:
        producto.agregar_stock(10)


class ProductoStockAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'cantidad',
        'precio_formateado',
        'costo_formateado',
        'ganancia_formateada'
    )

    actions = [agregar_stock_10]

    # 💰 FORMATO $
    def precio_formateado(self, obj):
        return f"${obj.precio_sugerido:,}".replace(",", ".")

    def costo_formateado(self, obj):
        return f"${obj.costo:,}".replace(",", ".")

    def ganancia_formateada(self, obj):
        return f"${obj.ganancia_unitaria():,}".replace(",", ".")

    precio_formateado.short_description = "Precio"
    costo_formateado.short_description = "Costo"
    ganancia_formateada.short_description = "Ganancia"


class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo', 'cantidad', 'fecha')
    list_filter = ('tipo', 'fecha')


admin.site.register(ProductoStock, ProductoStockAdmin)
admin.site.register(MovimientoStock, MovimientoStockAdmin)
