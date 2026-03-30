from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F
from django.db.models.functions import Coalesce

from .models import Pago, VentaPendiente


# =========================
# INLINE: Agregar abonos
# =========================
class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1
    fields = ('monto', 'descripcion', 'fecha')
    readonly_fields = ('fecha',)
    verbose_name = "Abono"
    verbose_name_plural = "Abonos / Pagos"


# =========================
# ADMIN: Ventas Pendientes de Pago
# =========================
@admin.register(VentaPendiente)
class VentaPendienteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'vendedor_display',
        'cliente',
        'campana_display',
        'productos_display',
        'total_formateado',
        'total_pagado_display',
        'saldo_display',
        'fecha',
    )
    list_filter = ('vendedor', 'campana', 'fecha')
    search_fields = ('cliente__nombre', 'vendedor__nombre')
    readonly_fields = ('cliente', 'vendedor', 'campana', 'fecha', 'total', 'resumen_pagos')
    inlines = [PagoInline]
    list_display_links = ('id', 'cliente')
    ordering = ('-fecha',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            total_pagado_ann=Coalesce(Sum('pago__monto'), 0)
        ).filter(total__gt=F('total_pagado_ann'))
        return qs

    def vendedor_display(self, obj):
        return obj.vendedor if obj.vendedor else "—"
    vendedor_display.short_description = "Vendedor"

    def campana_display(self, obj):
        return obj.campana if obj.campana else "— Stock —"
    campana_display.short_description = "Campaña"

    def productos_display(self, obj):
        productos = []
        for d in obj.detalleventa_set.all():
            productos.append(f"{d.producto_campana.producto.nombre} x{d.cantidad}")
        for d in obj.detalleventastock_set.all():
            productos.append(f"{d.producto_stock.nombre} x{d.cantidad}")
        return ", ".join(productos) if productos else "—"
    productos_display.short_description = "Productos"

    def total_formateado(self, obj):
        return format_html("<b>${}</b>", obj.total)
    total_formateado.short_description = "Total"

    def total_pagado_display(self, obj):
        pagado = obj.total_pagado()
        color = "green" if pagado > 0 else "gray"
        return format_html('<span style="color:{};">${}</span>', color, pagado)
    total_pagado_display.short_description = "Pagado"

    def saldo_display(self, obj):
        saldo = obj.saldo_pendiente()
        return format_html(
            '<span style="color:red; font-weight:bold;">${}</span>', saldo
        )
    saldo_display.short_description = "💰 Saldo Pendiente"

    def resumen_pagos(self, obj):
        pagos = obj.pago_set.all().order_by('fecha')
        if not pagos:
            return "Sin pagos registrados"
        filas = "".join([
            f"<tr><td>{p.fecha.strftime('%d/%m/%Y')}</td><td>${p.monto}</td><td>{p.descripcion or '—'}</td></tr>"
            for p in pagos
        ])
        return format_html(
            '<table style="width:100%; border-collapse:collapse;">'
            '<thead><tr><th>Fecha</th><th>Monto</th><th>Nota</th></tr></thead>'
            '<tbody>{}</tbody>'
            '</table>',
            filas
        )
    resumen_pagos.short_description = "Historial de Pagos"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# =========================
# ADMIN: Historial de Pagos
# =========================
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'fecha',
        'vendedor_display',
        'cliente',
        'campana_display',
        'productos_display',
        'total_venta',
        'monto_formateado',
        'saldo_display',
        'descripcion',
    )
    list_filter = ('fecha', 'venta__vendedor')
    search_fields = ('venta__cliente__nombre', 'venta__vendedor__nombre', 'descripcion')
    ordering = ('-fecha',)

    def vendedor_display(self, obj):
        return obj.venta.vendedor if obj.venta.vendedor else "—"
    vendedor_display.short_description = "Vendedor"

    def cliente(self, obj):
        return obj.venta.cliente
    cliente.short_description = "Cliente"

    def campana_display(self, obj):
        return obj.venta.campana if obj.venta.campana else "— Stock —"
    campana_display.short_description = "Campaña"

    def productos_display(self, obj):
        productos = []
        for d in obj.venta.detalleventa_set.all():
            productos.append(f"{d.producto_campana.producto.nombre} x{d.cantidad}")
        for d in obj.venta.detalleventastock_set.all():
            productos.append(f"{d.producto_stock.nombre} x{d.cantidad}")
        return ", ".join(productos) if productos else "—"
    productos_display.short_description = "Productos"

    def total_venta(self, obj):
        return format_html("<b>${}</b>", obj.venta.total)
    total_venta.short_description = "Total Venta"

    def monto_formateado(self, obj):
        return format_html('<span style="color:green;">${}</span>', obj.monto)
    monto_formateado.short_description = "Monto Pagado"

    def saldo_display(self, obj):
        saldo = obj.venta.saldo_pendiente()
        color = "red" if saldo > 0 else "green"
        texto = f"${saldo}" if saldo > 0 else "✅ Pagado"
        return format_html('<span style="color:{};">{}</span>', color, texto)
    saldo_display.short_description = "Saldo Restante"
