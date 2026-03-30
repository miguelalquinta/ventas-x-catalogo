from django.http import JsonResponse
from .models import ProductoCampana

def producto_campana_api(request, pk):
    try:
        pc = ProductoCampana.objects.get(pk=pk)

        data = {
            'precio': pc.precio,
            'costo': pc.costo
        }

        return JsonResponse(data)

    except ProductoCampana.DoesNotExist:
        return JsonResponse({'error': 'No existe'}, status=404)
