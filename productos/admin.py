from django.contrib import admin
from .models import Producto, ProductoCampana


class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa')
    search_fields = ('nombre',)


class ProductoCampanaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'campana', 'precio_formateado', 'costo_formateado', 'ganancia_formateada')
    list_filter = ('campana',)
    search_fields = ('producto__nombre',)

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


admin.site.register(Producto, ProductoAdmin)
admin.site.register(ProductoCampana, ProductoCampanaAdmin)