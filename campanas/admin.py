from django.contrib import admin
from django.utils.html import format_html
from .models import Campana


@admin.register(Campana)
class CampanaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'estado_display')
    list_filter = ('activa',)
    search_fields = ('nombre',)
    actions = ['cerrar_campanas', 'reabrir_campanas']

    def estado_display(self, obj):
        if obj.activa:
            return format_html(
                '<span style="color:green; font-weight:bold;">✅ Activa</span>'
            )
        return format_html(
            '<span style="color:red; font-weight:bold;">🔒 Cerrada</span>'
        )
    estado_display.short_description = "Estado"

    @admin.action(description="🔒 Cerrar campañas seleccionadas")
    def cerrar_campanas(self, request, queryset):
        cantidad = queryset.update(activa=False)
        self.message_user(request, f"{cantidad} campaña(s) cerrada(s). Sus productos ya no estarán disponibles en nuevas ventas.")

    @admin.action(description="✅ Reabrir campañas seleccionadas")
    def reabrir_campanas(self, request, queryset):
        cantidad = queryset.update(activa=True)
        self.message_user(request, f"{cantidad} campaña(s) reactivada(s).")
