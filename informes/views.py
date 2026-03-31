from django.shortcuts import render
from django.db.models import Sum, Count

def get_models():
    from ventas.models import Venta, DetalleVenta, DetalleVentaStock
    from pagos.models import Pago
    from campanas.models import Campana
    from clientes.models import Cliente
    from productos.models import Producto, ProductoCampana
    return {
        'Venta': Venta, 'DetalleVenta': DetalleVenta, 'DetalleVentaStock': DetalleVentaStock,
        'Pago': Pago, 'Campana': Campana, 'Cliente': Cliente, 'Producto': Producto, 'ProductoCampana': ProductoCampana
    }

def home(request):
    models = get_models()
    Cliente = models['Cliente']
    clientes_count = Cliente.objects.count()
    return render(request, 'informes/home.html', {'clientes_count': clientes_count})

def clientes_list(request):
    models = get_models()
    clientes = models['Cliente'].objects.all().order_by('nombre')
    return render(request, 'informes/clientes.html', {'clientes': clientes})

def productos_list(request):
    models = get_models()
    productos = models['Producto'].objects.all().order_by('nombre')
    return render(request, 'informes/productos.html', {'productos': productos})

def ventas_list(request):
    models = get_models()
    ventas = models['Venta'].objects.all().order_by('-fecha')
    return render(request, 'informes/ventas.html', {'ventas': ventas})

def pagos_list(request):
    models = get_models()
    pagos = models['Pago'].objects.all().order_by('-fecha')
    return render(request, 'informes/pagos.html', {'pagos': pagos})

def campanas_list(request):
    models = get_models()
    campanas = models['Campana'].objects.all().order_by('-fecha_inicio')
    return render(request, 'informes/campanas.html', {'campanas': campanas})

def deudas_list(request):
    models = get_models()
    ventas = models['Venta'].objects.filter(saldo__gt=0).order_by('cliente')
    return render(request, 'informes/deudas.html', {'ventas': ventas})
