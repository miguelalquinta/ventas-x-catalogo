from django.shortcuts import render
from django.http import JsonResponse
from .models import Venta
from productos.models import ProductoCampana


def lista_ventas(request):
    ventas = Venta.objects.all().order_by('-fecha')
    return render(request, 'ventas/lista.html', {'ventas': ventas})


def api_productos_por_campana(request, campana_id):
    """Devuelve los productos de una campaña en formato JSON para el filtrado dinámico."""
    productos = ProductoCampana.objects.filter(
        campana_id=campana_id,
        campana__activa=True
    ).select_related('producto')

    data = [
        {
            'id': p.id,
            'nombre': str(p.producto.nombre),
            'precio': float(p.precio),
            'costo': float(p.producto.costo),
        }
        for p in productos
    ]
    return JsonResponse({'productos': data})
