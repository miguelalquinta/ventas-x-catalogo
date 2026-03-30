from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Venta, DetalleVenta, DetalleVentaStock
from productos.models import ProductoCampana


# =========================
# WIDGET PERSONALIZADO
# =========================
class ProductoCampanaSelectWidget(forms.Select):
    """
    Select widget que añade data-campana-id a cada opción.
    Permite al JavaScript filtrar dinámicamente por campaña sin AJAX.
    Usa optgroups() para mayor compatibilidad con distintas versiones de Django.
    """
    def __init__(self, campana_map=None, *args, **kwargs):
        self.campana_map = campana_map or {}
        super().__init__(*args, **kwargs)

    def optgroups(self, name, value, attrs=None):
        groups = super().optgroups(name, value, attrs)
        for group_name, subgroup, index in groups:
            for option in subgroup:
                option_value = option.get('value')
                if option_value not in (None, ''):
                    try:
                        pk = int(str(option_value))
                        campana_id = self.campana_map.get(pk)
                        if campana_id is not None:
                            option['attrs']['data-campana-id'] = str(campana_id)
                    except (ValueError, TypeError):
                        pass
        return groups


# =========================
# INLINE STOCK
# =========================
class DetalleVentaStockInline(admin.TabularInline):
    model = DetalleVentaStock
    extra = 1
    fields = ('producto_stock', 'cantidad', 'precio', 'ver_costo', 'ver_subtotal', 'ver_ganancia')
    readonly_fields = ('ver_costo', 'ver_subtotal', 'ver_ganancia')

    def ver_costo(self, obj):
        if obj.pk:
            return format_html('<b>${}</b>', obj.costo)
        return format_html('<span class="campo-costo">$0</span>')

    def ver_subtotal(self, obj):
        if obj.pk:
            return format_html('<b>${}</b>', obj.subtotal)
        return format_html('<span class="campo-subtotal">$0</span>')

    def ver_ganancia(self, obj):
        if obj.pk:
            valor = obj.ganancia()
            color = 'green' if valor >= 0 else 'red'
            return format_html('<b style="color:{};">${}</b>', color, valor)
        return format_html('<span class="campo-ganancia">$0</span>')

    ver_costo.short_description = "Costo"
    ver_subtotal.short_description = "Subtotal"
    ver_ganancia.short_description = "Ganancia"


# =========================
# INLINE CATÁLOGO
# =========================
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ('producto_campana', 'cantidad', 'ver_precio', 'ver_costo', 'ver_subtotal', 'ver_ganancia')
    readonly_fields = ('ver_precio', 'ver_costo', 'ver_subtotal', 'ver_ganancia')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'producto_campana':
            # Cargar todos los productos de campañas activas
            qs = ProductoCampana.objects.filter(
                campana__activa=True
            ).select_related('campana', 'producto')
            kwargs['queryset'] = qs

            field = super().formfield_for_foreignkey(db_field, request, **kwargs)

            # Construir mapa {producto_id: campana_id} para el widget
            campana_map = {pc.id: pc.campana_id for pc in qs}

            # Reemplazar el widget para que cada <option> tenga data-campana-id
            field.widget = ProductoCampanaSelectWidget(
                campana_map=campana_map,
                attrs=field.widget.attrs,
            )
            return field
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def ver_precio(self, obj):
        if obj.pk and obj.producto_campana_id:
            return format_html('<b>${}</b>', obj.producto_campana.precio)
        return format_html('<span class="campo-precio">$0</span>')

    def ver_costo(self, obj):
        if obj.pk:
            return format_html('<b>${}</b>', obj.costo)
        return format_html('<span class="campo-costo">$0</span>')

    def ver_subtotal(self, obj):
        if obj.pk:
            return format_html('<b>${}</b>', obj.subtotal)
        return format_html('<span class="campo-subtotal">$0</span>')

    def ver_ganancia(self, obj):
        if obj.pk:
            valor = obj.ganancia()
            color = 'green' if valor >= 0 else 'red'
            return format_html('<b style="color:{};">${}</b>', color, valor)
        return format_html('<span class="campo-ganancia">$0</span>')

    ver_precio.short_description = "Precio"
    ver_costo.short_description = "Costo"
    ver_subtotal.short_description = "Subtotal"
    ver_ganancia.short_description = "Ganancia"


# =========================
# ADMIN VENTA
# =========================
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'vendedor', 'campana_display', 'fecha', 'total', 'total_pagado_display', 'saldo_display')
    list_filter = ('vendedor', 'campana', 'fecha')
    search_fields = ('cliente__nombre', 'vendedor__nombre')
    inlines = [DetalleVentaInline, DetalleVentaStockInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'campana':
            from campanas.models import Campana
            kwargs['queryset'] = Campana.objects.filter(activa=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def campana_display(self, obj):
        if not obj.campana:
            return "— Stock —"
        if obj.campana.activa:
            return format_html('✅ {}', obj.campana.nombre)
        return format_html('<span style="color:gray;">🔒 {}</span>', obj.campana.nombre)
    campana_display.short_description = "Campaña"

    def total_pagado_display(self, obj):
        pagado = obj.total_pagado()
        color = "green" if pagado > 0 else "gray"
        return format_html('<span style="color:{};">${}</span>', color, pagado)
    total_pagado_display.short_description = "Pagado"

    def saldo_display(self, obj):
        saldo = obj.saldo_pendiente()
        if saldo <= 0:
            return format_html('<span style="color:green;">✅ Pagado</span>')
        return format_html('<span style="color:red; font-weight:bold;">${}</span>', saldo)
    saldo_display.short_description = "Saldo"

    class Media:
        js = ('ventas/js/autocompletar_producto.js',)
