from django.urls import path
from .views import lista_ventas, api_productos_por_campana

urlpatterns = [
    path('', lista_ventas, name='lista_ventas'),
    path('api/productos-campana/<int:campana_id>/', api_productos_por_campana, name='api_productos_por_campana'),
]