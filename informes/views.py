from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from ventas.models import Venta, DetalleVenta, DetalleVentaStock
from pagos.models import Pago
from stock.models import ProductoStock
from catalogo.models import ProductoCampana
from campanas.models import Campana
from clientes.models import Cliente
from vendedores.models import Vendedor
from productos.models import Producto
import csv

def informes_home(request):
    return render(request, 'informes/home.html')

def clientes_informe(request):
    clientes = Cliente.objects.annotate(
        total_ventas=Count('venta'),
        total_vendido=Sum('venta__total'),
        total_pagado=Sum('venta__pagos__monto')
    )
    return render(request, 'informes/clientes.html', {'clientes': clientes})

def productos_informe(request):
    return render(request, 'informes/productos.html')

def ventas_informe(request):
    ventas = Venta.objects.select_related('cliente', 'vendedor').all()
    return render(request, 'informes/ventas.html', {'ventas': ventas})

def pagos_informe(request):
    pagos = Pago.objects.select_related('venta', 'venta__cliente').all()
    return render(request, 'informes/pagos.html', {'pagos': pagos})

def campanas_informe(request):
    campanas = Campana.objects.all()
    return render(request, 'informes/campanas.html', {'campanas': campanas})

def deudas_informe(request):
    return render(request, 'informes/deudas.html')
