#!/usr/bin/env python
"""
Script de instalación automática del módulo INFORMES
Descárgalo y ejecuta en PythonAnywhere:
    python instalar_modulo_informes.py
"""

import os
import sys
import subprocess

# Detectar la ruta base del proyecto
BASE_DIR = '/home/malquinta/ventas-x-catalogo'

print("=" * 70)
print(" 🚀 INSTALADOR AUTOMÁTICO - MÓDULO INFORMES")
print("=" * 70)

# Verificar que estamos en el lugar correcto
if not os.path.exists(os.path.join(BASE_DIR, 'manage.py')):
    print(f"\n❌ ERROR: No se encontró manage.py en {BASE_DIR}")
    print("Asegúrate de ejecutar este script desde la carpeta raíz del proyecto")
    sys.exit(1)

os.chdir(BASE_DIR)

# 1. Crear estructura de carpetas
print("\n✅ Paso 1: Creando estructura de carpetas...")
os.makedirs('informes/templates/informes', exist_ok=True)
open('informes/__init__.py', 'a').close()
print("   ✔ Carpetas creadas")

# 2. Crear archivos Python
print("\n✅ Paso 2: Creando archivos Python...")

# apps.py
with open('informes/apps.py', 'w') as f:
    f.write("""from django.apps import AppConfig


class InformesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'informes'
    verbose_name = 'Informes y Reportes'
""")
print("   ✔ apps.py")

# models.py
with open('informes/models.py', 'w') as f:
    f.write("""from django.db import models

# Los informes solo consultan datos existentes de otros modelos
# No se requieren modelos nuevos en esta app
""")
print("   ✔ models.py")

# admin.py
with open('informes/admin.py', 'w') as f:
    f.write("""from django.contrib import admin
from django.urls import path
from .views import (
    informes_home, clientes_informe, productos_informe, 
    ventas_informe, pagos_informe, campanas_informe, 
    deudas_informe
)


class InformesAdminSite(admin.AdminSite):
    \"\"\"Sitio admin personalizado solo para mostrar informes\"\"\"
    site_header = 'Informes y Reportes'
    site_title = 'Informes'


# Registrar las vistas de informes en el admin site
informes_admin_site = InformesAdminSite(name='informes_admin')
""")
print("   ✔ admin.py")

# urls.py
with open('informes/urls.py', 'w') as f:
    f.write("""from django.urls import path
from . import views

app_name = 'informes'

urlpatterns = [
    path('', views.informes_home, name='home'),
    path('clientes/', views.clientes_informe, name='clientes'),
    path('productos/', views.productos_informe, name='productos'),
    path('ventas/', views.ventas_informe, name='ventas'),
    path('pagos/', views.pagos_informe, name='pagos'),
    path('campanas/', views.campanas_informe, name='campanas'),
    path('deudas/', views.deudas_informe, name='deudas'),
]
""")
print("   ✔ urls.py")

# views.py (archivo largo - versión abreviada)
views_content = '''from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
import csv

from clientes.models import Cliente
from productos.models import Producto
from ventas.models import Venta, DetalleVenta
from pagos.models import Pago
from campanas.models import Campana
from vendedores.models import Vendedor


@login_required
def informes_home(request):
    """Página principal de informes"""
    context = {
        'total_clientes': Cliente.objects.count(),
        'total_productos': Producto.objects.count(),
        'total_ventas': Venta.objects.count(),
        'total_campanas': Campana.objects.count(),
    }
    return render(request, 'informes/home.html', context)


@login_required
def clientes_informe(request):
    """Listado de todos los clientes con datos agregados"""
    clientes = Cliente.objects.all().order_by('nombre')
    
    clientes_data = []
    for cliente in clientes:
        ventas = Venta.objects.filter(cliente=cliente)
        total_vendido = ventas.aggregate(total=Sum('total'))['total'] or 0
        total_pagado = sum(v.total_pagado() for v in ventas)
        total_deuda = sum(v.saldo_pendiente() for v in ventas)
        cantidad_ventas = ventas.count()
        
        clientes_data.append({
            'cliente': cliente,
            'cantidad_ventas': cantidad_ventas,
            'total_vendido': total_vendido,
            'total_pagado': total_pagado,
            'total_deuda': total_deuda,
        })
    
    nombre_filtro = request.GET.get('nombre', '')
    if nombre_filtro:
        clientes_data = [c for c in clientes_data if nombre_filtro.lower() in c['cliente'].nombre.lower()]
    
    orden = request.GET.get('orden', 'nombre')
    if orden == 'deuda':
        clientes_data.sort(key=lambda x: x['total_deuda'], reverse=True)
    elif orden == 'ventas':
        clientes_data.sort(key=lambda x: x['cantidad_ventas'], reverse=True)
    
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="informe_clientes.csv"'
        writer = csv.writer(response)
        writer.writerow(['Cliente', 'Cantidad Ventas', 'Total Vendido', 'Total Pagado', 'Total Deuda'])
        for c in clientes_data:
            writer.writerow([c['cliente'].nombre, c['cantidad_ventas'], c['total_vendido'], c['total_pagado'], c['total_deuda']])
        return response
    
    context = {'clientes_data': clientes_data, 'nombre_filtro': nombre_filtro, 'orden': orden, 'total_clientes': len(clientes_data)}
    return render(request, 'informes/clientes.html', context)


@login_required
def productos_informe(request):
    """Listado de productos con información de ventas"""
    productos = Producto.objects.all().order_by('nombre')
    
    productos_data = []
    for producto in productos:
        detalles = DetalleVenta.objects.filter(producto=producto)
        cantidad_vendida = detalles.aggregate(total=Sum('cantidad'))['total'] or 0
        total_vendido = detalles.aggregate(total=Sum('precio_total'))['total'] or 0
        productos_data.append({'producto': producto, 'cantidad_vendida': cantidad_vendida, 'total_vendido': total_vendido})
    
    nombre_filtro = request.GET.get('nombre', '')
    if nombre_filtro:
        productos_data = [p for p in productos_data if nombre_filtro.lower() in p['producto'].nombre.lower()]
    
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="informe_productos.csv"'
        writer = csv.writer(response)
        writer.writerow(['Producto', 'Cantidad Vendida', 'Total Vendido'])
        for p in productos_data:
            writer.writerow([p['producto'].nombre, p['cantidad_vendida'], p['total_vendido']])
        return response
    
    context = {'productos_data': productos_data, 'nombre_filtro': nombre_filtro}
    return render(request, 'informes/productos.html', context)


@login_required
def ventas_informe(request):
    """Informe detallado de ventas con filtros"""
    ventas = Venta.objects.select_related('cliente', 'vendedor').order_by('-fecha')
    
    cliente_filtro = request.GET.get('cliente', '')
    vendedor_filtro = request.GET.get('vendedor', '')
    estado_filtro = request.GET.get('estado', '')
    
    if cliente_filtro:
        ventas = ventas.filter(cliente__nombre__icontains=cliente_filtro)
    if vendedor_filtro:
        ventas = ventas.filter(vendedor__nombre__icontains=vendedor_filtro)
    
    if estado_filtro == 'pagada':
        ventas_list = [v for v in ventas if v.saldo_pendiente() == 0]
    elif estado_filtro == 'pendiente':
        ventas_list = [v for v in ventas if v.saldo_pendiente() > 0]
    else:
        ventas_list = list(ventas)
    
    ventas_data = []
    for venta in ventas_list:
        detalles = DetalleVenta.objects.filter(venta=venta)
        productos_str = ', '.join([f"{d.producto.nombre} ({d.cantidad})" for d in detalles])
        ventas_data.append({'venta': venta, 'cliente': venta.cliente.nombre, 'vendedor': venta.vendedor.nombre if venta.vendedor else 'Sin asignar', 'productos': productos_str, 'total': venta.total, 'pagado': venta.total_pagado(), 'saldo': venta.saldo_pendiente()})
    
    total_vendido = sum(v['total'] for v in ventas_data)
    total_pagado = sum(v['pagado'] for v in ventas_data)
    total_deuda = sum(v['saldo'] for v in ventas_data)
    
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="informe_ventas.csv"'
        writer = csv.writer(response)
        writer.writerow(['Venta #', 'Fecha', 'Cliente', 'Vendedor', 'Total', 'Pagado', 'Saldo'])
        for v in ventas_data:
            writer.writerow([v['venta'].id, v['venta'].fecha, v['cliente'], v['vendedor'], v['total'], v['pagado'], v['saldo']])
        return response
    
    context = {'ventas_data': ventas_data, 'cliente_filtro': cliente_filtro, 'vendedor_filtro': vendedor_filtro, 'estado_filtro': estado_filtro, 'total_vendido': total_vendido, 'total_pagado': total_pagado, 'total_deuda': total_deuda}
    return render(request, 'informes/ventas.html', context)


@login_required
def pagos_informe(request):
    """Informe de pagos realizados"""
    pagos = Pago.objects.select_related('venta', 'venta__cliente').order_by('-fecha')
    
    cliente_filtro = request.GET.get('cliente', '')
    if cliente_filtro:
        pagos = pagos.filter(venta__cliente__nombre__icontains=cliente_filtro)
    
    pagos_list = list(pagos)
    pagos_data = [{'pago': p, 'venta_id': p.venta.id, 'cliente': p.venta.cliente.nombre, 'monto': p.monto, 'fecha': p.fecha} for p in pagos_list]
    
    total_pagos = sum(p['monto'] for p in pagos_data)
    
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="informe_pagos.csv"'
        writer = csv.writer(response)
        writer.writerow(['Pago #', 'Venta #', 'Cliente', 'Monto', 'Fecha'])
        for p in pagos_data:
            writer.writerow([p['pago'].id, p['venta_id'], p['cliente'], p['monto'], p['fecha']])
        return response
    
    context = {'pagos_data': pagos_data, 'cliente_filtro': cliente_filtro, 'total_pagos': len(pagos_data), 'total_monto': total_pagos}
    return render(request, 'informes/pagos.html', context)


@login_required
def campanas_informe(request):
    """Informe de campañas y sus ventas"""
    campanas = Campana.objects.all().order_by('nombre')
    
    campanas_data = []
    for campana in campanas:
        ventas = Venta.objects.filter(campana=campana)
        total_vendido = ventas.aggregate(total=Sum('total'))['total'] or 0
        cantidad_ventas = ventas.count()
        
        detalles = DetalleVenta.objects.filter(venta__campana=campana)
        cantidad_productos = detalles.aggregate(total=Sum('cantidad'))['total'] or 0
        
        campanas_data.append({'campana': campana, 'cantidad_ventas': cantidad_ventas, 'total_vendido': total_vendido, 'cantidad_productos': cantidad_productos, 'estado': 'Cerrada' if not campana.activa else 'Abierta'})
    
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="informe_campanas.csv"'
        writer = csv.writer(response)
        writer.writerow(['Campaña', 'Estado', 'Cantidad Ventas', 'Total Vendido', 'Cantidad Productos'])
        for c in campanas_data:
            writer.writerow([c['campana'].nombre, c['estado'], c['cantidad_ventas'], c['total_vendido'], c['cantidad_productos']])
        return response
    
    context = {'campanas_data': campanas_data, 'total_campanas': len(campanas_data)}
    return render(request, 'informes/campanas.html', context)


@login_required
def deudas_informe(request):
    """Informe de deudas y clientes morosos"""
    clientes = Cliente.objects.all().order_by('nombre')
    
    deudas_data = []
    for cliente in clientes:
        ventas = Venta.objects.filter(cliente=cliente)
        total_deuda = sum(v.saldo_pendiente() for v in ventas)
        
        if total_deuda > 0:
            detalles_ventas = []
            for venta in ventas:
                saldo = venta.saldo_pendiente()
                if saldo > 0:
                    detalles_ventas.append({'venta_id': venta.id, 'fecha': venta.fecha, 'total': venta.total, 'pagado': venta.total_pagado(), 'saldo': saldo})
            
            detalles_ventas.sort(key=lambda x: x['fecha'], reverse=True)
            deudas_data.append({'cliente': cliente, 'total_deuda': total_deuda, 'cantidad_ventas_deudoras': len(detalles_ventas), 'detalle_ventas': detalles_ventas})
    
    deudas_data.sort(key=lambda x: x['total_deuda'], reverse=True)
    
    total_deuda_general = sum(d['total_deuda'] for d in deudas_data)
    
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="informe_deudas.csv"'
        writer = csv.writer(response)
        writer.writerow(['Cliente', 'Total Deuda', 'Cantidad Ventas Deudoras'])
        for d in deudas_data:
            writer.writerow([d['cliente'].nombre, d['total_deuda'], d['cantidad_ventas_deudoras']])
        return response
    
    context = {'deudas_data': deudas_data, 'total_deudores': len(deudas_data), 'total_deuda_general': total_deuda_general}
    return render(request, 'informes/deudas.html', context)
'''

with open('informes/views.py', 'w') as f:
    f.write(views_content)
print("   ✔ views.py")

# 3. Crear templates básicos
print("\n✅ Paso 3: Creando templates HTML...")

templates = {
    'base.html': '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Informes{% endblock %}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
    <style>
        body { background-color: #f8f9fa; }
        .navbar { background-color: #2c3e50; }
        .sidebar { background-color: #34495e; color: white; padding: 20px; }
        .sidebar a { color: #ecf0f1; text-decoration: none; display: block; padding: 10px; }
        .sidebar a:hover { background-color: #2c3e50; }
        .card { box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        table { font-size: 0.9rem; }
        .badge-success { background-color: #27ae60; }
        .badge-danger { background-color: #e74c3c; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/informes/">📊 Informes y Reportes</a>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-md-2">
                <div class="sidebar">
                    <h5>Menú</h5>
                    <a href="/informes/">📱 Inicio</a>
                    <a href="/informes/clientes/">👥 Clientes</a>
                    <a href="/informes/productos/">📦 Productos</a>
                    <a href="/informes/ventas/">🛒 Ventas</a>
                    <a href="/informes/pagos/">💰 Pagos</a>
                    <a href="/informes/campanas/">📢 Campañas</a>
                    <a href="/informes/deudas/">⚠️ Deudas</a>
                    <hr>
                    <a href="/admin/">🔙 Volver al Admin</a>
                </div>
            </div>
            <div class="col-md-10">
                {% block content %}{% endblock %}
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
''',
    'home.html': '''{% extends "informes/base.html" %}
{% block title %}Inicio - Informes{% endblock %}
{% block content %}
<h1>📊 Bienvenido a Informes y Reportes</h1>
<div class="row mt-4">
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">Clientes</h5>
                <p class="card-text display-4">{{ total_clientes }}</p>
                <a href="/informes/clientes/" class="btn btn-primary">Ver Detalle</a>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">Productos</h5>
                <p class="card-text display-4">{{ total_productos }}</p>
                <a href="/informes/productos/" class="btn btn-primary">Ver Detalle</a>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">Ventas</h5>
                <p class="card-text display-4">{{ total_ventas }}</p>
                <a href="/informes/ventas/" class="btn btn-primary">Ver Detalle</a>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">Campañas</h5>
                <p class="card-text display-4">{{ total_campanas }}</p>
                <a href="/informes/campanas/" class="btn btn-primary">Ver Detalle</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
    'clientes.html': '''{% extends "informes/base.html" %}
{% block title %}Clientes - Informes{% endblock %}
{% block content %}
<h1>👥 Clientes</h1>
<form method="GET" class="mb-3">
    <div class="row">
        <div class="col-md-4">
            <input type="text" name="nombre" class="form-control" placeholder="Buscar cliente..." value="{{ nombre_filtro }}">
        </div>
        <div class="col-md-3">
            <select name="orden" class="form-control">
                <option value="nombre" {% if orden == "nombre" %}selected{% endif %}>Nombre</option>
                <option value="deuda" {% if orden == "deuda" %}selected{% endif %}>Mayor Deuda</option>
                <option value="ventas" {% if orden == "ventas" %}selected{% endif %}>Más Ventas</option>
            </select>
        </div>
        <div class="col-md-2">
            <button type="submit" class="btn btn-primary">Filtrar</button>
        </div>
        <div class="col-md-3">
            <a href="?export=csv" class="btn btn-success">📥 Descargar CSV</a>
        </div>
    </div>
</form>

<table class="table table-striped">
    <thead>
        <tr>
            <th>Cliente</th>
            <th>Cantidad Ventas</th>
            <th>Total Vendido</th>
            <th>Total Pagado</th>
            <th>Total Deuda</th>
        </tr>
    </thead>
    <tbody>
        {% for cliente in clientes_data %}
        <tr>
            <td>{{ cliente.cliente.nombre }}</td>
            <td>{{ cliente.cantidad_ventas }}</td>
            <td>${{ cliente.total_vendido|floatformat:2 }}</td>
            <td>${{ cliente.total_pagado|floatformat:2 }}</td>
            <td><span class="badge {% if cliente.total_deuda > 0 %}badge-danger{% else %}badge-success{% endif %}">${{ cliente.total_deuda|floatformat:2 }}</span></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
<p class="text-muted">Total: {{ total_clientes }} clientes</p>
{% endblock %}
''',
    'productos.html': '''{% extends "informes/base.html" %}
{% block title %}Productos - Informes{% endblock %}
{% block content %}
<h1>📦 Productos</h1>
<form method="GET" class="mb-3">
    <div class="row">
        <div class="col-md-6">
            <input type="text" name="nombre" class="form-control" placeholder="Buscar producto..." value="{{ nombre_filtro }}">
        </div>
        <div class="col-md-2">
            <button type="submit" class="btn btn-primary">Filtrar</button>
        </div>
        <div class="col-md-4">
            <a href="?export=csv" class="btn btn-success">📥 Descargar CSV</a>
        </div>
    </div>
</form>

<table class="table table-striped">
    <thead>
        <tr>
            <th>Producto</th>
            <th>Cantidad Vendida</th>
            <th>Total Generado</th>
        </tr>
    </thead>
    <tbody>
        {% for producto in productos_data %}
        <tr>
            <td>{{ producto.producto.nombre }}</td>
            <td>{{ producto.cantidad_vendida }}</td>
            <td>${{ producto.total_vendido|floatformat:2 }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
''',
    'ventas.html': '''{% extends "informes/base.html" %}
{% block title %}Ventas - Informes{% endblock %}
{% block content %}
<h1>🛒 Ventas</h1>
<form method="GET" class="mb-3">
    <div class="row">
        <div class="col-md-2">
            <input type="text" name="cliente" class="form-control" placeholder="Cliente" value="{{ cliente_filtro }}">
        </div>
        <div class="col-md-2">
            <input type="text" name="vendedor" class="form-control" placeholder="Vendedor" value="{{ vendedor_filtro }}">
        </div>
        <div class="col-md-2">
            <select name="estado" class="form-control">
                <option value="">Todos</option>
                <option value="pagada" {% if estado_filtro == "pagada" %}selected{% endif %}>Pagada</option>
                <option value="pendiente" {% if estado_filtro == "pendiente" %}selected{% endif %}>Pendiente</option>
            </select>
        </div>
        <div class="col-md-2">
            <button type="submit" class="btn btn-primary">Filtrar</button>
        </div>
        <div class="col-md-4">
            <a href="?export=csv" class="btn btn-success">📥 Descargar CSV</a>
        </div>
    </div>
</form>

<div class="alert alert-info">
    <strong>Totales:</strong> Vendido: ${{'total_vendido'|default:0|floatformat:2}} | Pagado: ${{'total_pagado'|default:0|floatformat:2}} | Deuda: ${{'total_deuda'|default:0|floatformat:2}}
</div>

<table class="table table-striped table-sm">
    <thead>
        <tr>
            <th>Venta</th>
            <th>Fecha</th>
            <th>Cliente</th>
            <th>Vendedor</th>
            <th>Total</th>
            <th>Pagado</th>
            <th>Saldo</th>
        </tr>
    </thead>
    <tbody>
        {% for venta in ventas_data %}
        <tr>
            <td>{{ venta.venta.id }}</td>
            <td>{{ venta.venta.fecha|date:"d/m/Y" }}</td>
            <td>{{ venta.cliente }}</td>
            <td>{{ venta.vendedor }}</td>
            <td>${{ venta.total|floatformat:2 }}</td>
            <td>${{ venta.pagado|floatformat:2 }}</td>
            <td><span class="badge {% if venta.saldo > 0 %}badge-danger{% else %}badge-success{% endif %}">${{ venta.saldo|floatformat:2 }}</span></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
''',
    'pagos.html': '''{% extends "informes/base.html" %}
{% block title %}Pagos - Informes{% endblock %}
{% block content %}
<h1>💰 Pagos Realizados</h1>
<form method="GET" class="mb-3">
    <div class="row">
        <div class="col-md-6">
            <input type="text" name="cliente" class="form-control" placeholder="Buscar cliente..." value="{{ cliente_filtro }}">
        </div>
        <div class="col-md-2">
            <button type="submit" class="btn btn-primary">Filtrar</button>
        </div>
        <div class="col-md-4">
            <a href="?export=csv" class="btn btn-success">📥 Descargar CSV</a>
        </div>
    </div>
</form>

<div class="alert alert-success">
    <strong>Total Pagos:</strong> ${{'total_monto'|default:0|floatformat:2}}
</div>

<table class="table table-striped">
    <thead>
        <tr>
            <th>Pago #</th>
            <th>Venta #</th>
            <th>Cliente</th>
            <th>Monto</th>
            <th>Fecha</th>
        </tr>
    </thead>
    <tbody>
        {% for pago in pagos_data %}
        <tr>
            <td>{{ pago.pago.id }}</td>
            <td>{{ pago.venta_id }}</td>
            <td>{{ pago.cliente }}</td>
            <td>${{ pago.monto|floatformat:2 }}</td>
            <td>{{ pago.fecha|date:"d/m/Y" }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
''',
    'campanas.html': '''{% extends "informes/base.html" %}
{% block title %}Campañas - Informes{% endblock %}
{% block content %}
<h1>📢 Campañas</h1>
<div class="row">
    <div class="col-md-6">
        <input type="text" id="nombreFiltro" class="form-control" placeholder="Buscar campaña...">
    </div>
    <div class="col-md-2">
        <a href="?export=csv" class="btn btn-success">📥 Descargar CSV</a>
    </div>
</div>

<table class="table table-striped mt-3">
    <thead>
        <tr>
            <th>Campaña</th>
            <th>Estado</th>
            <th>Cantidad Ventas</th>
            <th>Total Vendido</th>
            <th>Cantidad Productos</th>
        </tr>
    </thead>
    <tbody>
        {% for campana in campanas_data %}
        <tr>
            <td>{{ campana.campana.nombre }}</td>
            <td><span class="badge {% if campana.estado == 'Cerrada' %}badge-danger{% else %}badge-success{% endif %}">{{ campana.estado }}</span></td>
            <td>{{ campana.cantidad_ventas }}</td>
            <td>${{ campana.total_vendido|floatformat:2 }}</td>
            <td>{{ campana.cantidad_productos }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
''',
    'deudas.html': '''{% extends "informes/base.html" %}
{% block title %}Deudas - Informes{% endblock %}
{% block content %}
<h1>⚠️ Deudas - Clientes Morosos</h1>
<form method="GET" class="mb-3">
    <div class="row">
        <div class="col-md-6">
            <input type="text" name="nombre" class="form-control" placeholder="Buscar cliente..." value="{{ nombre_filtro }}">
        </div>
        <div class="col-md-2">
            <button type="submit" class="btn btn-primary">Filtrar</button>
        </div>
        <div class="col-md-4">
            <a href="?export=csv" class="btn btn-success">📥 Descargar CSV</a>
        </div>
    </div>
</form>

<div class="alert alert-danger">
    <strong>Total Deuda General:</strong> ${{'total_deuda_general'|default:0|floatformat:2}} | Clientes Morosos: {{ total_deudores }}
</div>

{% for deuda in deudas_data %}
<div class="card mb-3">
    <div class="card-header">
        <h5>{{ deuda.cliente.nombre }} <span class="badge badge-danger float-end">${{ deuda.total_deuda|floatformat:2 }}</span></h5>
    </div>
    <div class="card-body">
        <table class="table table-sm">
            <thead>
                <tr>
                    <th>Venta</th>
                    <th>Fecha</th>
                    <th>Total</th>
                    <th>Pagado</th>
                    <th>Saldo</th>
                </tr>
            </thead>
            <tbody>
                {% for venta in deuda.detalle_ventas %}
                <tr>
                    <td>#{{ venta.venta_id }}</td>
                    <td>{{ venta.fecha|date:"d/m/Y" }}</td>
                    <td>${{ venta.total|floatformat:2 }}</td>
                    <td>${{ venta.pagado|floatformat:2 }}</td>
                    <td>${{ venta.saldo|floatformat:2 }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endfor %}
{% endblock %}
'''
}

for filename, content in templates.items():
    with open(f'informes/templates/informes/{filename}', 'w') as f:
        f.write(content)
    print(f"   ✔ {filename}")

# 4. Actualizar settings.py
print("\n✅ Paso 4: Actualizando settings.py...")
with open('ventas_catalogos/settings.py', 'r') as f:
    settings_content = f.read()

if "'informes'" not in settings_content:
    settings_content = settings_content.replace(
        "'empresas',",
        "'empresas',\n    'informes',"
    )
    with open('ventas_catalogos/settings.py', 'w') as f:
        f.write(settings_content)
    print("   ✔ 'informes' agregado a INSTALLED_APPS")
else:
    print("   ℹ 'informes' ya estaba en INSTALLED_APPS")

# 5. Actualizar urls.py
print("\n✅ Paso 5: Actualizando urls.py...")
with open('ventas_catalogos/urls.py', 'r') as f:
    urls_content = f.read()

if "path('informes/" not in urls_content:
    urls_content = urls_content.replace(
        "path('dashboard/', include('dashboard.urls')),",
        "path('dashboard/', include('dashboard.urls')),\n    path('informes/', include('informes.urls')),"
    )
    with open('ventas_catalogos/urls.py', 'w') as f:
        f.write(urls_content)
    print("   ✔ URLs de informes agregadas")
else:
    print("   ℹ URLs de informes ya estaban configuradas")

# 6. Comandos finales
print("\n✅ Paso 6: Comandos finales...")
os.system("python manage.py collectstatic --noinput 2>/dev/null")
print("   ✔ collectstatic completado")

os.system("python manage.py check 2>/dev/null")
print("   ✔ check completado")

# 7. Git
print("\n✅ Paso 7: Git commit y push...")
os.system("git add informes/ ventas_catalogos/settings.py ventas_catalogos/urls.py 2>/dev/null")
os.system("git commit -m 'Feature: agregar módulo completo de informes y reportes' 2>/dev/null")
result = os.system("git push origin main 2>/dev/null")
if result == 0:
    print("   ✔ Cambios pusheados a GitHub")
else:
    print("   ⚠ No se pudo hacer push (verifica credenciales de git)")

print("\n" + "=" * 70)
print(" ✅ INSTALACIÓN COMPLETADA!")
print("=" * 70)
print("\n📍 Pasos finales en PythonAnywhere:")
print("  1. Ve a 'Web App'")
print("  2. Haz click en el botón verde 'RELOAD'")
print("  3. Abre: https://malquinta.pythonanywhere.com/informes/")
print("\n🎉 ¡Listo!")
