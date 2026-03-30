from django.contrib import admin
from .models import Cliente


class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'deuda')
    search_fields = ('nombre', 'telefono')

    def deuda(self, obj):
        return f"${obj.deuda_total():,}".replace(",", ".")

    deuda.short_description = "Deuda"


admin.site.register(Cliente, ClienteAdmin)
