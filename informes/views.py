from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta

def informes_home(request):
    return render(request, 'informes/home.html')

def clientes_informe(request):
    from clientes.models import Cliente
    clientes = Cliente.objects.all()
    return render(request, 'informes/clientes.html', {'clientes': clientes})

def productos_informe(request):
    return render(request, 'informes/productos.html')

def ventas_informe(request):
    from ventas.models import Venta
    ventas = Venta.objects.all()
    return render(request, 'informes/ventas.html', {'ventas': ventas})

def pagos_informe(request):
    from pagos.models import Pago
    pagos = Pago.objects.all()
    return render(request, 'informes/pagos.html', {'pagos': pagos})

def campanas_informe(request):
    from campanas.models import Campana
    campanas = Campana.objects.all()
    return render(request, 'informes/campanas.html', {'campanas': campanas})

def deudas_informe(request):
    return render(request, 'informes/deudas.html')
