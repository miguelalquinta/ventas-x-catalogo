from django.http import JsonResponse
from .models import ProductoStock


def producto_api(request, pk):
    producto = ProductoStock.objects.get(pk=pk)

    data = {
        'precio_sugerido': producto.precio_sugerido,
        'costo': producto.costo
    }

    return JsonResponse(data)