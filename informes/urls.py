from django.urls import path
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
