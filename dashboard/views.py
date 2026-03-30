from django.shortcuts import render
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.utils import timezone

from ventas.models import Venta, DetalleVenta, DetalleVentaStock
from pagos.models import Pago
from campanas.models import Campana
from vendedores.models import Vendedor
from clientes.models import Cliente
from stock.models import ProductoStock
from productos.models import ProductoCampana, Producto
import json


def _is_mobile(request):
    """Detecta si es un dispositivo móvil."""
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'windows phone', 'blackberry']
    return any(keyword in user_agent for keyword in mobile_keywords)


def dashboard(request):
    """Dashboard principal con todas las métricas."""
    
    # =====================================================
    # 🎯 KPIs PRINCIPALES
    # =====================================================
    
    # 💰 Total vendido
    total_vendido = Venta.objects.aggregate(total=Sum('total'))['total'] or 0
    
    # 💸 Total cobrado
    total_cobrado = Pago.objects.aggregate(total=Sum('monto'))['total'] or 0
    
    # 📉 Total deuda
    total_deuda = total_vendido - total_cobrado
    
    # 📈 Ganancia total
    ganancia_catalogo = sum(
        (d.producto_campana.precio - d.costo) * d.cantidad
        for d in DetalleVenta.objects.all()
    )
    ganancia_stock = sum(
        (d.precio - d.costo) * d.cantidad
        for d in DetalleVentaStock.objects.all()
    )
    ganancia_total = ganancia_catalogo + ganancia_stock
    
    # =====================================================
    # 📊 DATOS PARA GRÁFICOS
    # =====================================================
    
    # 📦 Productos más vendidos (top 10)
    productos_mas_vendidos = []
    
    # Top de catálogo
    top_catalogo = DetalleVenta.objects.values(
        'producto_campana__producto__nombre'
    ).annotate(
        total_cantidad=Sum('cantidad'),
        total_ganancia=Sum(F('cantidad') * (F('producto_campana__precio') - F('costo')))
    ).order_by('-total_cantidad')[:10]
    
    # Top de stock
    top_stock = DetalleVentaStock.objects.values(
        'producto_stock__nombre'
    ).annotate(
        total_cantidad=Sum('cantidad'),
        total_ganancia=Sum(F('cantidad') * (F('precio') - F('costo')))
    ).order_by('-total_cantidad')[:10]
    
    for item in top_catalogo:
        productos_mas_vendidos.append({
            'nombre': item['producto_campana__producto__nombre'],
            'cantidad': item['total_cantidad'],
            'ganancia': int(item['total_ganancia'] or 0),
        })
    
    for item in top_stock:
        productos_mas_vendidos.append({
            'nombre': item['producto_stock__nombre'],
            'cantidad': item['total_cantidad'],
            'ganancia': int(item['total_ganancia'] or 0),
        })
    
    # Ordenar y tomar top 10 combinados
    productos_mas_vendidos = sorted(productos_mas_vendidos, key=lambda x: x['cantidad'], reverse=True)[:10]
    
    # 📅 Ventas por mes (últimos 6 meses)
    hace_6_meses = timezone.now() - timedelta(days=180)
    ventas_por_mes = Venta.objects.filter(
        fecha__gte=hace_6_meses
    ).annotate(
        mes=TruncMonth('fecha')
    ).values('mes').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('mes')
    
    meses = []
    totales_mes = []
    for item in ventas_por_mes:
        if item['mes']:
            meses.append(item['mes'].strftime('%b %Y'))
            totales_mes.append(item['total'])
    
    # 🎪 Ventas por campaña
    ventas_por_campana = Venta.objects.exclude(
        campana__isnull=True
    ).values('campana__nombre').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('-total')
    
    campanas_nombres = [v['campana__nombre'] for v in ventas_por_campana]
    campanas_totales = [v['total'] for v in ventas_por_campana]
    
    # 👨‍💼 Ventas por vendedor
    ventas_por_vendedor = Venta.objects.exclude(
        vendedor__isnull=True
    ).values('vendedor__nombre').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('-total')
    
    vendedores_nombres = [v['vendedor__nombre'] for v in ventas_por_vendedor]
    vendedores_totales = [v['total'] for v in ventas_por_vendedor]
    
    # =====================================================
    # 📋 TABLAS DETALLADAS
    # =====================================================
    
    # 👥 Top clientes con más deuda
    clientes_con_deuda = []
    for cliente in Cliente.objects.all():
        deuda = cliente.deuda_total()
        if deuda > 0:
            clientes_con_deuda.append({
                'nombre': cliente.nombre,
                'deuda': deuda,
                'telefono': cliente.telefono or '-',
            })
    
    clientes_con_deuda = sorted(clientes_con_deuda, key=lambda x: x['deuda'], reverse=True)[:15]
    
    # 🎂 Cumpleaños próximos (dentro de 7 días)
    from django.db.models import Q
    from datetime import date
    
    hoy = date.today()
    proxima_semana = hoy + timedelta(days=7)
    
    cumpleanos_proximos = []
    for cliente in Cliente.objects.filter(fecha_nacimiento__isnull=False):
        if cliente.fecha_nacimiento:
            # Obtener mes y día del cumpleaños
            mes_cumple = cliente.fecha_nacimiento.month
            dia_cumple = cliente.fecha_nacimiento.day
            
            # Crear fecha de cumpleaños para este año
            fecha_cumple_este_ano = date(hoy.year, mes_cumple, dia_cumple)
            
            # Si ya pasó este año, considerar el próximo
            if fecha_cumple_este_ano < hoy:
                fecha_cumple_este_ano = date(hoy.year + 1, mes_cumple, dia_cumple)
            
            # Verificar si está dentro de los próximos 7 días
            if hoy <= fecha_cumple_este_ano <= proxima_semana:
                edad = hoy.year - cliente.fecha_nacimiento.year
                if fecha_cumple_este_ano.month < hoy.month or \
                   (fecha_cumple_este_ano.month == hoy.month and fecha_cumple_este_ano.day < hoy.day):
                    edad += 1
                
                cumpleanos_proximos.append({
                    'nombre': cliente.nombre,
                    'fecha': fecha_cumple_este_ano,
                    'edad': edad,
                    'telefono': cliente.telefono or '-',
                    'dias_falta': (fecha_cumple_este_ano - hoy).days,
                })
    
    cumpleanos_proximos = sorted(cumpleanos_proximos, key=lambda x: x['dias_falta'])
    
    # 📦 Stock bajo (cantidad < 10)
    stock_bajo = ProductoStock.objects.filter(
        cantidad__lt=10
    ).order_by('cantidad').values(
        'nombre', 'cantidad', 'precio_sugerido', 'costo'
    )
    
    # 📝 Últimas 20 ventas
    ultimas_ventas = Venta.objects.select_related(
        'cliente', 'vendedor', 'campana'
    ).order_by('-fecha')[:20]
    
    # =====================================================
    # 📤 CONTEXTO PARA TEMPLATE
    # =====================================================
    
    context = {
        # KPIs
        'total_vendido': total_vendido,
        'total_cobrado': total_cobrado,
        'total_deuda': total_deuda,
        'ganancia_total': ganancia_total,
        
        # Porcentajes
        'pct_cobrado': round((total_cobrado / total_vendido * 100) if total_vendido > 0 else 0, 1),
        
        # Gráficos
        'meses_json': json.dumps(meses),
        'totales_mes_json': json.dumps(totales_mes),
        'campanas_nombres_json': json.dumps(campanas_nombres),
        'campanas_totales_json': json.dumps(campanas_totales),
        'vendedores_nombres_json': json.dumps(vendedores_nombres),
        'vendedores_totales_json': json.dumps(vendedores_totales),
        'productos_json': json.dumps(
            [{'name': p['nombre'], 'cantidad': p['cantidad']} for p in productos_mas_vendidos]
        ),
        
        # Tablas
        'clientes_con_deuda': clientes_con_deuda,
        'cumpleanos_proximos': cumpleanos_proximos,
        'stock_bajo': stock_bajo,
        'ultimas_ventas': ultimas_ventas,
        'productos_mas_vendidos': productos_mas_vendidos,
        'ventas_por_vendedor': ventas_por_vendedor,
        'ventas_por_campana': ventas_por_campana,
    }
    
    # Seleccionar template según dispositivo
    is_mobile = _is_mobile(request)
    template_name = 'dashboard/index_mobile.html' if is_mobile else 'dashboard/index.html'
    
    return render(request, template_name, context)
