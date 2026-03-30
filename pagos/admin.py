from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import JsonResponse
from .models import Pago, VentaPendiente
from ventas.models import Venta


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'venta', 'monto', 'fecha', 'ver_total_venta', 'ver_saldo_pendiente')
    list_filter = ('fecha',)
    search_fields = ('venta__cliente__nombre', 'venta__id')
    fields = ('venta', 'monto')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('api/venta-resumen/<int:venta_id>/', self.venta_resumen_api),
        ]
        return custom_urls + urls
    
    def venta_resumen_api(self, request, venta_id):
        try:
            venta = Venta.objects.get(id=venta_id)
            total = venta.total
            pagado = venta.total_pagado()
            saldo = venta.saldo_pendiente()
            porcentaje = int((pagado / total * 100)) if total > 0 else 0
            
            return JsonResponse({
                'cliente': venta.cliente.nombre,
                'total': f"{total:,}",
                'pagado': f"{pagado:,}",
                'saldo': f"{saldo:,}",
                'porcentaje': porcentaje
            })
        except Venta.DoesNotExist:
            return JsonResponse({'error': 'Venta no encontrada'}, status=404)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'venta':
            # Obtener IDs de ventas con saldo pendiente
            todas_ventas = Venta.objects.select_related('cliente').order_by('-fecha')
            ventas_pendientes_ids = [v.id for v in todas_ventas if v.saldo_pendiente() > 0]
            kwargs['queryset'] = Venta.objects.filter(id__in=ventas_pendientes_ids).select_related('cliente').order_by('-fecha')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def ver_total_venta(self, obj):
        return f"${obj.venta.total:,}"
    ver_total_venta.short_description = "Total Venta"
    
    def ver_saldo_pendiente(self, obj):
        saldo = obj.venta.saldo_pendiente()
        color = 'red' if saldo > 0 else 'green'
        return format_html(f'<span style="color: {color}; font-weight: bold;">${saldo:,}</span>')
    ver_saldo_pendiente.short_description = "Saldo Pendiente"


@admin.register(VentaPendiente)
class VentaPendienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'ver_total', 'ver_total_pagado', 'ver_saldo', 'fecha')
    list_filter = ('fecha',)
    search_fields = ('cliente__nombre',)
    readonly_fields = ('ver_total', 'ver_total_pagado', 'ver_saldo', 'resumen_pago', 'fecha')
    fieldsets = (
        ('Información de Venta', {
            'fields': ('cliente', 'vendedor', 'campana', 'fecha')
        }),
        ('Resumen de Pagos', {
            'fields': ('resumen_pago', 'ver_total', 'ver_total_pagado', 'ver_saldo'),
            'classes': ('wide',)
        }),
    )
    
    def ver_total(self, obj):
        return f"${obj.total:,}"
    ver_total.short_description = "💰 Total Venta"
    
    def ver_total_pagado(self, obj):
        pagado = obj.total_pagado()
        return format_html(f'<span style="color: green; font-weight: bold;">${pagado:,}</span>')
    ver_total_pagado.short_description = "✅ Total Pagado"
    
    def ver_saldo(self, obj):
        saldo = obj.saldo_pendiente()
        color = 'red' if saldo > 0 else 'green'
        return format_html(f'<span style="color: {color}; font-weight: bold;">${saldo:,}</span>')
    ver_saldo.short_description = "⚠️ Saldo Pendiente"
    
    def resumen_pago(self, obj):
        total = obj.total
        pagado = obj.total_pagado()
        saldo = obj.saldo_pendiente()
        porcentaje = int((pagado / total * 100)) if total > 0 else 0
        
        return format_html(
            f'''
            <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px;">
                <p><strong>RESUMEN DE PAGO</strong></p>
                <p>Total Venta: <strong style="color: blue;">${total:,}</strong></p>
                <p>Total Pagado: <strong style="color: green;">${pagado:,}</strong></p>
                <p>Saldo Pendiente: <strong style="color: red;">${saldo:,}</strong></p>
                <p>Porcentaje Pagado: <strong>{porcentaje}%</strong></p>
                <div style="background-color: #ddd; height: 20px; margin-top: 10px; border-radius: 3px; overflow: hidden;">
                    <div style="background-color: green; height: 100%; width: {porcentaje}%;"></div>
                </div>
            </div>
            '''
        )
    resumen_pago.short_description = "Resumen Detallado"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
